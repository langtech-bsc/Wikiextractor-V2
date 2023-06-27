# Python translator

import os
#from deep_translator import GoogleTranslator as translator
from deep_translator import GoogleTranslator as translator

""" 
from deep_translator import (GoogleTranslator,
                             MicrosoftTranslator,
                             PonsTranslator,
                             LingueeTranslator,
                             MyMemoryTranslator,
                             YandexTranslator,
                             PapagoTranslator,
                             DeeplTranslator,
                             QcriTranslator,
                             single_detection,
                             batch_detection)
"""




OUTPUT_FILE = "/home/arubio/bsc/Files/wikiextractor_all_banned_sections.txt"



source_lang = 'en'

# Banned sections
text_to_translate = [   'References',
                        'References and notes',
                        'Notes and references',
                        'See also',
                        'Gallery of images',
                        'External Links',
                        'Bibliography',
                        'Selected Bibliography',
                        'Complementary Bibliography',
                        'Works cited',
                        'Additional bibliography',
                        'Notes',
                        'Further reading',
                        'Exhibition Catalogues',
                        'Collections',
                        'Related sound files',
]



# All ISO-639-1 langs
dest_langs = ['aa', 'ab', 'af', 'am', 'ar', 'as', 'ay', 'az', 'ba', 'be', 'bg', 'bh', 'bi', 'bn', 'bo', 'br', 'ca', 'co', 'cs', 'cy', 'da', 'de', 'dz', 'el', 'en', 'eo', 'es', 'et', 'eu', 'fa', 'fi', 'fj', 'fo', 'fr', 'fy', 'ga', 'gd', 'gl', 'gn', 'gu', 'ha', 'he', 'hi', 'hr', 'hu', 'hy', 'ia', 'id', 'ie', 'ik', 'in', 'is', 'it', 'iw', 'ja', 'ji', 'jw', 'ka', 'kk', 'kl', 'km', 'kn', 'ko', 'ks', 'ku', 'ky', 'kz', 'la', 'ln', 'lo', 'ls', 'lt', 'lv', 'mg', 'mi', 'mk', 'ml', 'mn', 'mo', 'mr', 'ms', 'mt', 'my', 'na', 'ne', 'nl', 'no', 'oc', 'om', 'or', 'pa', 'pl', 'ps', 'pt', 'qu', 'rm', 'rn', 'ro', 'ru', 'rw', 'sa', 'sb', 'sd', 'sg', 'sh', 'si', 'sk', 'sl', 'sm', 'sn', 'so', 'sq', 'sr', 'ss', 'st', 'su', 'sv', 'sw', 'sx', 'ta', 'te', 'tg', 'th', 'ti', 'tk', 'tl', 'tn', 'to', 'tr', 'ts', 'tt', 'tw', 'uk', 'ur', 'us', 'uz', 'vi', 'vo', 'wo', 'xh', 'yi', 'yo', 'zh', 'zu']
#dest_langs = ['es', 'ca']


dest_text = { #langcode : [text_to_translate]


}




supported_langs = [v for k,v in translator().get_supported_languages(as_dict=True).items()]
# (len(v)==2) and 
langs_notgoingtobe_processed = [v for v in dest_langs if v not in supported_langs]
print('\n WARNING: NOT SUPPORTED LANGUAGES (Text it wont be translated to this ones):')



for v in langs_notgoingtobe_processed:
    print(v)



def translate_text(source_lang, dest_lang, text_to_translate ):

    #debug
    print('\t\t\t...' + dest_lang + '\n')
    
    final_text = "\n\n\n+ LANGUAGE (ISO-639-1): " + dest_lang + '\n'
    _text = ''
    for text in text_to_translate:
        _text += text + '\n'
        #final_text += translator(source=source_lang, target=dest_lang).translate(text=text) + '\n'
    final_text += translator(source=source_lang, target=dest_lang).translate(text=_text) 


    return final_text


print('\n\nTranslating...')

with open(OUTPUT_FILE,'w') as f:
    [f.write( translate_text(source_lang, dest_lang, text_to_translate ) ) for dest_lang in  dest_langs if dest_lang in supported_langs ]


print('DONE!')
print('File saved as:' + str( os.path.abspath(OUTPUT_FILE)   ))

