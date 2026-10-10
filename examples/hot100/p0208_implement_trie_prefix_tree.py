"""208 · 实现 Trie (前缀树)：原创教学实现。"""
class _TrieNode:
    def __init__(self):
        self.children = {}
        self.terminal = False

class Trie:
    def __init__(self):
        self.root = _TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = _TrieNode()
            node = node.children[char]
        # 路径存在仅代表前缀，完整单词另用终点标记。
        node.terminal = True

    def _walk(self, text):
        node = self.root
        for char in text:
            node = node.children.get(char)
            if node is None:
                return None
        return node

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return node is not None and node.terminal

    def startsWith(self, prefix: str) -> bool:
        return self._walk(prefix) is not None
