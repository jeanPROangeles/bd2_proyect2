from numpy import sqrt
from lib import *
import json
import io
import linecache
from nltk.tokenize.toktok import ToktokTokenizer
# >>> import nltk
# >>> nltk.download('perluniprops')
# >>> nltk.download('nonbreaking_prefixes')
from nltk.stem.snowball import SnowballStemmer


class DataRecovery():
    stopList = []
    stemmer = SnowballStemmer('spanish')
    tokenizer = ToktokTokenizer()

    def __init__(self):
        self.stopList.clear()
        with open(path_stop_list, 'r', encoding="utf-8") as file:
            self.stopList = [line.lower().strip() for line in file]
        file.close()

    def __getStem(self, word):
        return self.stemmer.stem(word.lower())

    def __save_in_file_aux(self, local_map, path):
        local_map_keys = local_map.keys()
        local_map_keys = sorted(local_map_keys)
        with open(path, 'w', encoding="utf-8") as file_aux_out:
            for key in local_map_keys:
                file_aux_out.write(json.dumps(
                    {key: local_map[key]}, ensure_ascii=False))
                file_aux_out.write("\n")
            file_aux_out.close()

    def __save_in_file_norm(self, frecuency_map, id):
        with open(path_norm_doc, 'a', encoding="utf-8") as file_norm_out:
            sum = 0
            for key in frecuency_map:
                sum = sum + frecuency_map[key] * frecuency_map[key]
            sum = sqrt(sum)
            file_norm_out.write(json.dumps({id: sum}, ensure_ascii=False))
            file_norm_out.write("\n")
            file_norm_out.close()

    def load(self, name_file_to_load):
        local_map = {}
        size_of_local_map = 0
        id_file_aux = 1
        with open(path_data_in + name_file_to_load, 'r', encoding="utf-8") as file_to_load:
            for tweet in file_to_load:
                tweet = tweet.rstrip()
                json_tweet = json.load(io.StringIO(tweet))
                tweet_id = json_tweet.get("id")
                tweet_text = json_tweet.get("text").lower() if json_tweet.get(
                    "RT_text") == None else json_tweet.get("RT_text").lower()
                tweet_words = self.tokenizer.tokenize(tweet_text)
                # tweet_words = nltk.word_tokenize(tweet_text)
                frecuency_map = {}
                for tweet_word in tweet_words:
                    if tweet_word in self.stopList:
                        continue
                    # Especial case:
                    if tweet_word[:4] == "http":
                        continue
                    if tweet_word[-1] == '.':
                        tweet_word = tweet_word[:-1]
                    ###
                    tweet_word_root = self.__getStem(tweet_word)
                    if tweet_word_root in local_map:
                        if tweet_id in local_map[tweet_word_root]:
                            local_map[tweet_word_root][tweet_id] = local_map[tweet_word_root][tweet_id] + 1
                        else:
                            local_map[tweet_word_root][tweet_id] = 1
                            size_of_local_map = size_of_local_map + \
                                len(str(tweet_id)) + 6
                    else:
                        local_map[tweet_word_root] = {tweet_id: 1}
                        size_of_local_map = size_of_local_map + \
                            len(str(tweet_id)) + 1 + len(tweet_word_root) + 8
                    if size_of_local_map > MAX_TERMS_IN_MAP:
                        self.__save_in_file_aux(
                            local_map, path_file_aux + str(id_file_aux) + path_file_aux_end)
                        local_map.clear()
                        size_of_local_map = 0
                        id_file_aux = id_file_aux + 1
                    if tweet_word_root in frecuency_map:
                        frecuency_map[tweet_word_root] = frecuency_map[tweet_word_root] + 1
                    else:
                        frecuency_map[tweet_word_root] = 1
                self.__save_in_file_norm(frecuency_map, tweet_id)
            file_to_load.close()
        if len(local_map) > 0:
            self.__save_in_file_aux(local_map, path_file_aux +
                                    str(id_file_aux) + path_file_aux_end)
        # Una vez generado los aux, unificarlos. Hay id_file_aux
        # Por cada id_file_aux, generar un buffer de lectura
        read_buffer = []
        line_buffer = []
        for i in range(id_file_aux):
            line = linecache.getline(
                path_file_aux + str(i+1) + path_file_aux_end, 4).rstrip()
            if line == "":
                continue
            term = json.load(io.StringIO(line))
            keys = list(term.keys())
            read_buffer.append([keys[0], list(term.get(keys[0]))])
            line_buffer.append(1)

        print(read_buffer)
        print(line_buffer)
