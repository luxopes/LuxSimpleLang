import datetime, math, random, time, re, os, shutil
from tkinter import simpledialog

class SimpleLangInterpreter:
    def __init__(self, output_callback):
        self.print_output = output_callback
        self.variables = {}
        self.lines = []
        self.i = 0
        self.loop_stack = []
        self.if_stack = []
        self.functions = {}

    def remove_multiline_comments(self, code):
        # Odstraní víceřádkové komentáře typu /* ... */
        return re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)

    def run(self, code):
        self.variables = {}
        # Nejprve odstraníme víceřádkové komentáře
        code = self.remove_multiline_comments(code)
        self.lines = code.strip().splitlines()
        self.i = 0
        self.loop_stack = []
        self.if_stack = []
        self.functions = {}
        self.find_functions()
        self.i = 0
        while self.i < len(self.lines):
            line = self.lines[self.i].strip()
            self.execute_line(line)
            self.i += 1

    def find_functions(self):
        i = 0
        while i < len(self.lines):
            line = self.lines[i].strip()
            if line.startswith("function "):
                name = line[len("function "):].strip().rstrip(":")
                start = i + 1
                depth = 1
                while i + 1 < len(self.lines) and depth > 0:
                    i += 1
                    inner_line = self.lines[i].strip()
                    if inner_line.startswith("function "):
                        depth += 1
                    elif inner_line in ("end", ";"):
                        depth -= 1
                self.functions[name] = (start, i - 1)
            i += 1

    def execute_line(self, line):
        if not line or line.startswith("#"):
            return

        # --- IF / ELSE ---
        if line.startswith("if "):
            condition = line[3:].strip().rstrip(":")
            result = bool(self.eval_expr(condition))
            self.if_stack.append(result)
            if not result:
                self.skip_block()
            return

        if line == "else:":
            if self.if_stack:
                last = self.if_stack.pop()
                new_val = not last
                self.if_stack.append(new_val)
                if last:  # předtím byla pravda, přeskočíme else
                    self.skip_block()
            return

        if line == "end" or line == ";":
            if self.loop_stack:
                loop_type, start_index = self.loop_stack[-1][:2]
                if loop_type == "count":
                    count = self.loop_stack[-1][2] - 1
                    if count > 0:
                        self.loop_stack[-1] = (loop_type, start_index, count)
                        self.i = start_index
                    else:
                        self.loop_stack.pop()
                elif loop_type == "while_n":
                    n_val = self.variables.get("n", 0)
                    if n_val > 0:
                        self.i = start_index
                    else:
                        self.loop_stack.pop()
                elif loop_type == "while_cond":
                    condition = self.loop_stack[-1][2]
                    if bool(self.eval_expr(condition)):
                        self.i = start_index
                    else:
                        self.loop_stack.pop()
                elif loop_type == "for":
                    varname, endval = self.loop_stack[-1][2:]
                    current = self.variables.get(varname, None)
                    if current is not None and current < endval:
                        self.variables[varname] = current + 1
                        self.i = start_index
                    else:
                        self.loop_stack.pop()
            elif self.if_stack:
                self.if_stack.pop()
            return

        # --- LOOPS ---
        if line.startswith("loop "):
            expr = line[5:].replace(":", "").strip()
            value = self.eval_expr(expr)
            if isinstance(value, int):
                if expr == "n":
                    self.loop_stack.append(("while_n", self.i))
                else:
                    self.loop_stack.append(("count", self.i, value))
            else:
                self.print_output("[Error: Invalid loop value]")
            return

        if line.startswith("while "):
            condition = line[6:].strip().rstrip(":")
            if bool(self.eval_expr(condition)):
                self.loop_stack.append(("while_cond", self.i, condition))
            else:
                self.skip_block()
            return

        if line.startswith("for "):
            # syntaxis: for i in 1..10:
            m = re.match(r'for\s+(\w+)\s+in\s+(\S+)\.\.(\S+):?', line)
            if m:
                varname, start, end = m.groups()
                start_val = int(self.eval_expr(start))
                end_val = int(self.eval_expr(end))
                self.variables[varname] = start_val
                self.loop_stack.append(("for", self.i, varname, end_val))
            else:
                self.print_output("[Error: Invalid for syntax]")
            return

        if line.startswith("break"):
            if self.loop_stack:
                self.skip_loop()
            return

        if line.startswith("continue"):
            if self.loop_stack:
                self.i = self.loop_stack[-1][1]
            return

        # --- PRINT ---
        if line.startswith("print "):
            expr = line[6:].strip()
            result = self.eval_expr(expr)
            self.print_output(str(result))
            return

        # --- CALL FUNCTION ---
        if line.startswith("call "):
            func_name = line[5:].strip()
            if func_name in self.functions:
                start, end = self.functions[func_name]
                saved_i = self.i
                for i in range(start, end + 1):
                    self.execute_line(self.lines[i].strip())
                self.i = saved_i
            else:
                self.print_output(f"[Error: Unknown function '{func_name}']")
            return

        # --- FILE IO ---
        if line.startswith("readfile "):
            # readfile "soubor.xxx" -> proměnná _lastread
            fname = line[9:].strip().strip("\"'")
            if os.path.exists(fname):
                with open(fname, "r", encoding="utf-8") as f:
                    self.variables["_lastread"] = f.read()
            else:
                self.print_output(f"[Error: File '{fname}' not found]")
            return

        if line.startswith("writefile "):
            # writefile "soubor.xxx", vyraz
            parts = line[10:].split(",", 1)
            if len(parts) == 2:
                fname = parts[0].strip().strip("\"'")
                data = str(self.eval_expr(parts[1].strip()))
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(data)
            else:
                self.print_output("[Error: Invalid writefile syntax]")
            return

        if line.startswith("appendfile "):
            # appendfile "soubor.xxx", vyraz
            parts = line[11:].split(",", 1)
            if len(parts) == 2:
                fname = parts[0].strip().strip("\"'")
                data = str(self.eval_expr(parts[1].strip()))
                with open(fname, "a", encoding="utf-8") as f:
                    f.write(data)
            else:
                self.print_output("[Error: Invalid appendfile syntax]")
            return

        if line.startswith("createdir "):
            # createdir "cesta/ke/slozce"
            path = self.eval_expr(line[10:].strip())
            try:
                os.makedirs(str(path), exist_ok=True)
            except Exception as e:
                self.print_output(f"[Error creating directory: {e}]")
            return

        if line.startswith("listdir "):
            # listdir "cesta"
            path = self.eval_expr(line[8:].strip())
            try:
                files = os.listdir(str(path))
                for f in files:
                    full_path = os.path.join(str(path), f)
                    if os.path.isdir(full_path):
                        self.print_output(f"[DIR] {f}")
                    else:
                        self.print_output(f"[FILE] {f}")
            except Exception as e:
                self.print_output(f"[Error listing directory: {e}]")
            return

        if line.startswith("deletedir "):
            # deletedir "cesta"
            path = self.eval_expr(line[10:].strip())
            try:
                os.rmdir(str(path))  # rmdir smaže jen prázdnou složku
            except Exception as e:
                self.print_output(f"[Error deleting directory: {e}]")
            return

        # --- ASSIGNMENTS ---
        if "=" in line:
            var, expr = map(str.strip, line.split("=", 1))
            if expr.startswith("input "):
                prompt = expr[6:].strip().strip("\"")
                self.variables[var] = simpledialog.askstring("Input", prompt)
                return
            if expr.startswith("[") and expr.endswith("]"):
                try:
                    self.variables[var] = eval(expr, {"__builtins__": None}, {})
                except:
                    self.print_output(f"[Error: Invalid list syntax in '{line}']")
                return
            if expr == "date":
                self.variables[var] = datetime.date.today().isoformat()
                return
            self.variables[var] = self.eval_expr(expr)
            return

        # --- LIST OPERATIONS ---
        if line.startswith("append "):
            try:
                parts = line[7:].split(",", 1)
                list_name = parts[0].strip()
                value = self.eval_expr(parts[1].strip())
                if list_name in self.variables and isinstance(self.variables[list_name], list):
                    self.variables[list_name].append(value)
                else:
                    self.print_output(f"[Error: {list_name} is not a list]")
            except:
                self.print_output("[Error: Invalid append syntax]")
            return

        if line.startswith("remove "):
            try:
                parts = line[7:].split(",", 1)
                list_name = parts[0].strip()
                index = int(self.eval_expr(parts[1].strip()))
                if list_name in self.variables and isinstance(self.variables[list_name], list):
                    del self.variables[list_name][index]
                else:
                    self.print_output(f"[Error: {list_name} is not a list]")
            except:
                self.print_output("[Error: Invalid remove syntax]")
            return

    def skip_block(self):
        depth = 1
        while self.i + 1 < len(self.lines) and depth > 0:
            self.i += 1
            line = self.lines[self.i].strip()
            if line.startswith(("if ", "loop ", "while ", "for ", "function ")):
                depth += 1
            elif line in ("end", ";", "else:"):
                depth -= 1

    def skip_loop(self):
        if self.loop_stack:
            start = self.loop_stack[-1][1]
            depth = 1
            while self.i + 1 < len(self.lines) and depth > 0:
                self.i += 1
                line = self.lines[self.i].strip()
                if line.startswith(("loop ", "while ", "for ")):
                    depth += 1
                elif line in ("end", ";"):
                    depth -= 1
            self.loop_stack.pop()

    def eval_expr(self, expr):
        try:
            for var in self.variables:
                expr = re.sub(rf'\b{re.escape(var)}\b', repr(self.variables[var]), expr)
            local_env = {
                "math": math,
                "len": len,
                "str": str,
                "int": int,
                "rand": lambda a, b: random.randint(a, b),
                "sleep": time.sleep,
                "upper": lambda s: str(s).upper(),
                "lower": lambda s: str(s).lower(),
                "split": lambda s, sep=None: str(s).split(sep),
                "exists": lambda path: os.path.exists(str(path))
            }
            if expr == "date":
                return datetime.date.today().isoformat()
            return eval(expr, {"__builtins__": None}, local_env)
        except Exception as e:
            return f"[Error: {e}]"
