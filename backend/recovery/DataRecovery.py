from numpy import sqrt
from lib import *
import json
import io
from os import listdir, remove
from os.path import isfile, join
import linecache
from math import log10
from queue import PriorityQueue
from nltk.tokenize.toktok import ToktokTokenizer
# >>> import nltk
# >>> nltk.download('perluniprops')
# >>> nltk.download('nonbreaking_prefixes')
from nltk.stem.snowball import SnowballStemmer


class DataRecovery():
    stopList = []
    stemmer = SnowballStemmer('spanish')
    tokenizer = ToktokTokenizer()
    N = 0  # Cantidad de tweets

    def __init__(self):
        self.stopList.clear()
        with open(path_stop_list, 'r', encoding="utf-8") as file:
            self.stopList = [line.lower().strip() for line in file]
            file.close()
        # TODO: Añadir a N la cantidad de líneas de data/norm.json (tweets que ya fueron procesados)
        '''
        with open(path_norm_doc, 'r', encoding="utf-8") as file:
            num_lines = sum(1 for line in file)
            self.N = self.N + num_lines
            file.close()
        '''

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

    def __get_item_from_json_line(self, line):
        item_json = json.load(io.StringIO(line))
        keys = list(item_json.keys())
        return [keys[0], list(item_json.get(keys[0]).items())]

    def load(self):
        local_map = {}
        size_of_local_map = 0
        id_file_aux = 1
        print("Generando archivos auxiliares")
        for f in listdir(path_data_in):
            file_in = join(path_data_in, f)
            if isfile(file_in):
                with open(file_in, 'r', encoding="utf-8") as file_to_load:
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
                            if tweet_word[0] == '.':
                                tweet_word = tweet_word[1:]
                            if '.' in tweet_word:
                                pos = tweet_word.find('.')
                                rest_word = tweet_word[pos+1:]
                                if rest_word != "":
                                    tweet_words.append(rest_word)
                                tweet_word = tweet_word[:pos]
                            if 'covid' in tweet_word and tweet_word[0] == '#':
                                tweet_word = '#covid'
                            if 'covid' in tweet_word and tweet_word[0] != '#':
                                tweet_word = 'covid'
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
                                    len(str(tweet_id)) + 1 + \
                                    len(tweet_word_root) + 8
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
                        self.N = self.N + 1
                    file_to_load.close()
        if len(local_map) > 0:
            self.__save_in_file_aux(local_map, path_file_aux +
                                    str(id_file_aux) + path_file_aux_end)
        print(str(id_file_aux) +
              " archivos auxiliares generados. Generando archivo único")
        # Una vez generado los aux, unificarlos. Hay id_file_aux
        # Por cada id_file_aux, generar un buffer de lectura
        read_buffer = []
        number_of_line_buffer = []
        pq = PriorityQueue()
        buffer_remaining = []
        for i in range(id_file_aux):
            line = linecache.getline(
                path_file_aux + str(i+1) + path_file_aux_end, 1).rstrip()
            if line == "":
                continue
            read_buffer.append(self.__get_item_from_json_line(line))
            number_of_line_buffer.append(2)
            pq.put((read_buffer[i][0], i))
            buffer_remaining.append(i)
        # TODO: Añadir bufer de lectura de data/data.json
        with open(path_file_data, 'a', encoding="utf-8") as file:
            n = 0
            while not pq.empty():
                # Ver buffers y remaining buffers
                ''' 
                for pair in read_buffer:
                    print(pair[0])
                for id in buffer_remaining:
                    print(id, end="\t")
                print()
                '''
                term_dic = {}
                cur_term, cur_ind = pq.get()
                term_dic["name"] = cur_term
                term_dic["idf"] = 0
                term_dic["docs"] = []
                for pair in read_buffer[cur_ind][1]:
                    term_dic["docs"].append(pair)
                if cur_ind in buffer_remaining:
                    line = linecache.getline(
                        path_file_aux + str(cur_ind+1) + path_file_aux_end, number_of_line_buffer[cur_ind]).rstrip()
                    number_of_line_buffer[cur_ind] = number_of_line_buffer[cur_ind] + 1
                    if line == "":
                        buffer_remaining.remove(cur_ind)
                        # Borrar archivo aux
                        remove(path_file_aux + str(cur_ind + 1) +
                               path_file_aux_end)
                    else:
                        read_buffer[cur_ind] = self.__get_item_from_json_line(
                            line)
                        pq.put((read_buffer[cur_ind][0], cur_ind))
                # Mientras salga el mismo cur_term en pq.get, añado a local_map
                while not pq.empty():
                    cur_term_2, cur_ind_2 = pq.get()
                    if cur_term_2 != cur_term:
                        pq.put((cur_term_2, cur_ind_2))
                        break
                    for pair in read_buffer[cur_ind_2][1]:
                        term_dic["docs"].append(pair)
                    if cur_ind_2 in buffer_remaining:
                        line = linecache.getline(
                            path_file_aux + str(cur_ind_2+1) + path_file_aux_end, number_of_line_buffer[cur_ind_2]).rstrip()
                        number_of_line_buffer[cur_ind_2] = number_of_line_buffer[cur_ind_2] + 1
                        if line == "":
                            buffer_remaining.remove(cur_ind_2)
                            # Borrar archivo aux
                            remove(path_file_aux +
                                   str(cur_ind_2 + 1) + path_file_aux_end)
                        else:
                            read_buffer[cur_ind_2] = self.__get_item_from_json_line(
                                line)
                            pq.put((read_buffer[cur_ind_2][0], cur_ind_2))
                term_dic["idf"] = log10(self.N/len(term_dic["docs"]))
                file.write(json.dumps(term_dic, ensure_ascii=False))
                file.write("\n")
                n = n + 1
            #print("n: ", n)
            file.close()

    def score(self, query):
        pass
