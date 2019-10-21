#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import re
import shutil
import tempfile
import argparse
import json

def sedInplace(filename, pattern, repl):
    '''
    Perform the pure-Python equivalent of in-place `sed` substitution: e.g.,
    `sed -i -e 's/'${pattern}'/'${repl}' "${filename}"`.
    '''
    # For efficiency, precompile the passed regular expression.
    patternCompiled = re.compile(pattern.encode('utf-8'))

    # For portability, NamedTemporaryFile() defaults to mode "w+b" (i.e., binary
    # writing with updating). This is usually a good thing. In this case,
    # however, binary writing imposes non-trivial encoding constraints trivially
    # resolved by switching to text writing. Let's do that.
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmpFile:
        with open(filename) as srcFile:
            for line in srcFile:
                tmpFile.write(patternCompiled.sub(repl.encode('utf-8'), line))

    # Overwrite the original file with the munged temporary file in a
    # manner preserving file attributes (e.g., permissions).
    shutil.copystat(filename, tmpFile.name)
    shutil.move(tmpFile.name, filename)

class Translator:
    def __init__(self, lang):
        self.lang        = lang
        self.basePath    = os.path.dirname(os.path.abspath(__file__))
        self.opJsonFile  = self.basePath + "/op_i18n/%s.json" % self.lang
        self.apkJsonFile = self.basePath + "/apk_i18n/%s.json" % self.lang
        # 需要替换翻译信息的目录地址
        self.opPath      = self.basePath + "/openpilot/selfdrive/controls/lib"
        self.apkPath     = self.basePath + "/openpilot-apks"
        self.opFiles     = []
        self.apkFiles    = []
        self.opJson      = {}
        self.apkJson     = {}
        self.readJson()
        self.getFiles()

    def readJson(self):
        with open(self.opJsonFile) as f:
            self.opJson = json.load(f)
        with open(self.apkJsonFile) as f:
            self.apkJson = json.load(f)

    def getFiles(self):
        self.opFiles = self.getAllFileByPath(self.opPath)
        self.apkFiles = self.getAllFileByPath(self.apkPath)

    def run(self):
        for find, replace in self.opJson.iteritems():
            # print find, replace
            for f in self.opFiles:
                # print f.encode('utf-8')
                sedInplace(f, find, replace)

    def getAllFileByPath(self, path):
        files = []
        parents = os.listdir(path)
        for parent in parents:
            if parent[0] == ".": continue
            child = os.path.join(path, parent)
            # print os.path.isdir(child)
            if os.path.isdir(child):
                childFiles = self.getAllFileByPath(child)
                files.extend(childFiles)
            else:
                if child[0] == ".": continue
                # print(child.encode('utf-8'))
                files.append(child)
        return files

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', '-l', required=True, help='target language [zhs|zht]')
    args = parser.parse_args()
    # run translator
    worker = Translator(args.lang)
    worker.run()


