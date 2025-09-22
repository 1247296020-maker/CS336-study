from __future__ import annotations
import re
import regex
import torch
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple

from Demos.getfilever import pairs


class BPE:
    def __init__(self,max_vocab_size:int):
        self.vocab_size = 0 # 定义词汇表大小
        self.id_to_token ={} #: Dict[int,bytes]
        self.token_to_id ={} # Dict[bytes,int]
        self.merges = {}  #Dict[tuple[int,int],int]
        self.max_vocab_size = max_vocab_size

    def __initialize_vocab(self,special_tokens):
        for i in range(256):
            self.id_to_token[i] = bytes([i])
            self.token_to_id[bytes([i])] = i

        self.vocab_size = 256

        for token in special_tokens:
            token_new = token.encode("utf-8")
            if token_new not in self.token_to_id:
                self.token_to_id[token_new] = self.vocab_size
                self.id_to_token[self.vocab_size] = token_new
                self.vocab_size+=1

    def merge(self,list_word,pair:Tuple[int,int],new_index:int):
        a,b =pair
        out = []
        n =len(list_word)
        i = 0
        while i<n:
            if i+1< n and list_word[i] ==a and list_word[i+1] == b:
                out.append(new_index)
                i += 2
            else:
                out.append(list_word[i])
                i+=1
        return tuple(out)

    def train_byte_bpe(self,text,special_tokens):
        self.__initialize_vocab(special_tokens)
        escaped_tokens = [re.escape(token) for token in special_tokens]
        pattern = r"(" + "|".join(escaped_tokens) + r")"
        chunks = [c for c in re.split(pattern, text) if c != ""]

        PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
        all_word = defaultdict(int)
        #统计所有单词
        for chunk in chunks:
            for word in regex.findall(PAT,chunk):  #句子分为一个个单词

                bytes_word = tuple(word.encode("utf-8"))
                all_word[bytes_word]+=1

        while self.vocab_size < self.max_vocab_size:
            counts = defaultdict(int)
            for bytes_word ,frequence in all_word.items():
                for a, b in zip(bytes_word,bytes_word[1:]):
                    counts[(a,b)]+=frequence

            if not counts:break
            max_count = max(counts.values())
            canidates= [k for k,v in counts.items() if v == max_count]
            pair = max(canidates)
            new_token = self.id_to_token[pair[0]] + self.id_to_token[pair[1]]
            new_index =self.vocab_size
            self.vocab_size +=1
            self.merges[pair] = new_index
            self.token_to_id[new_token] = new_index
            self.id_to_token[new_index] = new_token


            new_all_word = defaultdict(int)
            for word,fre in all_word.items():
                word = self.merge(word,pair,new_index)
                new_all_word[word]=fre
            all_word = new_all_word


