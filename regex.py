class State:
    """Стан NFA з переходами на інші стани."""
    def __init__(self, name=None):
        self.name = name
        self.transitions = {}
        self.is_final = False

    def add_transition(self, symbol, state):
        """Додає перехід по символу (symbol=None для ε) до іншого стану."""
        if symbol in self.transitions:
            self.transitions[symbol].append(state)
        else:
            self.transitions[symbol] = [state]


class NFAFragment:
    """Допоміжна структура для фрагмента NFA з початковим і кінцевим станами."""
    def __init__(self, start, end):
        self.start = start
        self.end = end


def build_fragment_for_symbol(symbol):
    """Створює NFA-фрагмент для одного символу (букви/цифри чи '.')."""
    start = State()
    end = State()
    start.add_transition(symbol, end)
    return NFAFragment(start, end)


def apply_star_to_fragment(fragment):
    """
    Застосовує оператор '*' до фрагмента (нуль або більше повторень).
    Додаємо нові початковий і кінцевий стани з ε-переходами:
    - новий старт ε-> (старий старт) та ε-> (новий кінець) [можливість пропустити],
    - старий кінець ε-> (старий старт) (петля) та ε-> (новий кінець).
    """
    new_start = State()
    new_end = State()
    new_start.add_transition(None, fragment.start)
    new_start.add_transition(None, new_end)
    fragment.end.add_transition(None, fragment.start)
    fragment.end.add_transition(None, new_end)
    return NFAFragment(new_start, new_end)


def apply_plus_to_fragment(fragment):
    """
    Застосовує оператор '+' до фрагмента (один або більше повторень).
    Використовуємо існуючий старт фрагмента, додаємо новий кінець.
    Додаємо ε-перехід із старого кінця до старту (петля) і до нового кінця.
    """
    new_end = State()
    fragment.end.add_transition(None, fragment.start)
    fragment.end.add_transition(None, new_end)
    return NFAFragment(fragment.start, new_end)


class RegexFSM:
    """
    Клас для представлення регулярного виразу як скінченного автомата (NFA).
    Метод check_string перевіряє відповідність вхідного рядка цьому автомату.
    """
    def __init__(self, pattern):
        self.start_state = None
        self._build_nfa(pattern)

    def _build_nfa(self, pattern):
        base_start = None
        base_end = None
        i = 0
        n = len(pattern)

        while i < n:
            char = pattern[i]
            if char == '*' or char == '+':
                raise ValueError(f"Неприпустимий патерн: початок з '{char}'") 
            if char.isalnum() or char == '.':
                i += 1
                rep = None
                if i < n and pattern[i] in ('*', '+'):
                    rep = pattern[i]
                    i += 1
                fragment = build_fragment_for_symbol(char)
                if rep == '*':
                    fragment = apply_star_to_fragment(fragment)
                elif rep == '+':
                    fragment = apply_plus_to_fragment(fragment)
                if base_start is None:
                    base_start = fragment.start
                    base_end = fragment.end
                else:
                    base_end.add_transition(None, fragment.start)
                    base_end = fragment.end
            else:
                raise ValueError(f"Непідтримуваний символ у патерні: '{char}'")

        if base_start is None:
            base_start = State()
            base_end = base_start
        base_end.is_final = True
        self.start_state = base_start

    def epsilon_closure(self, states):
        """
        Обчислює ε-замикання множини станів
        """
        stack = list(states)
        closure = set(states)
        while stack:
            state = stack.pop()
            if None in state.transitions:
                for nxt in state.transitions[None]:
                    if nxt not in closure:
                        closure.add(nxt)
                        stack.append(nxt)
        return closure

    def check_string(self, input_str):
        """
        Перевіряє, чи належить input_str мові регулярного виразу.
        """
        current_states = self.epsilon_closure({self.start_state})
        for char in input_str:
            next_states = set()
            for state in current_states:
                if char in state.transitions:
                    next_states.update(state.transitions[char])
                if '.' in state.transitions:
                    next_states.update(state.transitions['.'])
            current_states = self.epsilon_closure(next_states)
        return any(state.is_final for state in current_states)

if __name__ == '__main__':
    fsm = RegexFSM('a*4.+hi')
    print(fsm.check_string('aaaaaa4uhi'))  # True
    print(fsm.check_string('4uhi'))       # True
    print(fsm.check_string('meow'))       # False
