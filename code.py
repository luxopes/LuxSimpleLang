import datetime, math, random, time, re
from tkinter import simpledialog  # kvůli inputům – zůstává, protože se používá i v CLI

class SimpleLangInterpreter:
    def __init__(self, output_callback):
        """
        output_callback – funkce, která dostane string a vytiskne/uloží ho.
        V GUI to bude Text.insert, v CLI třeba print.
        """
        self.print_output = output_callback
        self.variables = {}
        self.lines = []
        self.i = 0
        self.loop_stack = []
        self.if_stack = []
        self.functions = {}

    def run(self, code):
        self.variables = {}
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
                    elif inner_line == "end":
                        depth -= 1
                self.functions[name] = (start, i - 1)
            i += 1

    def execute_line(self, line):
        if not line or line.startswith("#"):
            return

        if line.startswith("if "):
            condition = line[3:].strip().rstrip(":")
            result = self.eval_expr(condition)
            self.if_stack.append(bool(result))
            if not result:
                self.skip_block()
            return

        if line == "else:":
            if self.if_stack:
                last = self.if_stack.pop()
                self.if_stack.append(not last)
                if last:
                    self.skip_block()
            return

        if line == "end":
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
            elif self.if_stack:
                self.if_stack.pop()
            return

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
            result = bool(self.eval_expr(condition))
            if not result:
                self.skip_block()
            else:
                self.loop_stack.append(("while_cond", self.i, condition))
            return

        if line.startswith("break"):
            if self.loop_stack:
                self.skip_loop()
            return

        if line.startswith("continue"):
            if self.loop_stack:
                self.i = self.loop_stack[-1][1]
            return

        if line.startswith("print "):
            expr = line[6:].strip()
            result = self.eval_expr(expr)
            self.print_output(str(result))
            return

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
            if line.startswith("if ") or line.startswith("loop ") or line.startswith("while ") or line.startswith("function "):
                depth += 1
            elif line == "end" or line == "else:":
                depth -= 1

    def skip_loop(self):
        if self.loop_stack:
            start = self.loop_stack[-1][1]
            depth = 1
            while self.i + 1 < len(self.lines) and depth > 0:
                self.i += 1
                line = self.lines[self.i].strip()
                if line.startswith("loop ") or line.startswith("while "):
                    depth += 1
                elif line == "end":
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
                "sleep": time.sleep
            }
            if expr == "date":
                return datetime.date.today().isoformat()
            return eval(expr, {"__builtins__": None}, local_env)
        except Exception as e:
            return f"[Error: {e}]"

