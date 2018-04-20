#!/usr/bin/env python
# coding=utf-8

import base64

def testEncryption():
	s1 = base64.encodestring('chuth-7?7vephaJere')
	s2 = base64.decodestring(s1)
	print s1,s2
	ddd=[decodestr(s1)]
	print ddd
	pass

def decodestr(s):
    return base64.decodestring(s)
    pass

def main():
	testEncryption()
	pass


if __name__ == '__main__':
	main()
	pass