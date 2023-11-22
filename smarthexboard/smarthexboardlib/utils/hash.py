import hashlib


def stable_hash(text: str) -> int:
	hash = 0
	for ch in text:
		hash = (hash * 281 ^ ord(ch) * 997) & 0xFFFFFFFF
	return hash
