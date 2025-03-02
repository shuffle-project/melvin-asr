import torch
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import SeamlessM4TTokenizer, SeamlessM4Tv2ForTextToText

device = "cuda"  # "cuda" or "cpu"
model_name = "facebook/seamless-m4t-v2-large"

tokenizer = SeamlessM4TTokenizer.from_pretrained(model_name, cache_dir="models")
model = SeamlessM4Tv2ForTextToText.from_pretrained(
    model_name,
    cache_dir="models",
)
print(model.config)
model.config.max_new_tokens = 512
print(model.config)
model.to(device)

text = "But the middle son was little and lorn he was neither dark nor fair he was neither handsome nor strong. Throwing himself on his knees before the King, he cried, Oh, royal Sire, bestow upon me also a sword and a steed, that I may up and away to follow my brethren. But the King laughed him to scorn. Thou a sword he quoth. In sooth thou shalt have one, but it shall be one befitting thy maiden size and courage, if so small a weapon can be found in all my kingdom Forthwith the grinning Jester began shrieking with laughter, so that the bells upon his motley cap were all set a jangling. I did but laugh to think the sword of Ethelried had been so quickly found, responded the Jester, and he pointed to the scissors hanging from the Tailor's girdle. One night as he lay in a deep forest, too unhappy to sleep, he heard a noise near at hand in the bushes. Thou shalt have thy liberty, he cried, even though thou shouldst rend me in pieces the moment thou art free. It had suddenly disappeared, and in its place stood a beautiful Fairy with filmy wings, which shone like rainbows in the moonlight. At this moment there was a distant rumbling as of thunder. 'Tis the Ogre cried the Fairy. We must hasten. Scissors, grow a giant's height And save us from the Ogre's might He could see the Ogre standing powerless to hurt him, on the other side of the chasm, and gnashing his teeth, each one of which was as big as a millston. The sight was so terrible, that he turned on his heel, and fled away as fast as his feet could carry him. Thou shalt not be left a prisoner in this dismal spot while I have the power to help thee. He lifted the scissors and with one stroke destroyed the web, and gave the Fly its freedom. A faint glimmer of light on the opposite wall shows me the keyhole. The Prince spent all the following time until midnight, trying to think of a suitable verse to say to the scissors. As he uttered the words the scissors leaped out of his hand, and began to cut through the wooden shutters as easily as through a cheese. In a very short time the Prince had crawled through the opening. While he stood looking around him in bewilderment, a Firefly alighted on his arm. Flashing its little lantern in the Prince's face, it cried, This way My friend, the Fly, sent me to guide you to a place of safety. What is to become of me? cried the poor peasant. My grain must fall and rot in the field from overripeness because I have not the strength to rise and harvest it then indeed must we all starve. The grandame whom he supplied with fagots, the merchant whom he rescued from robbers, the King's councillor to whom he gave aid, all became his friends. Up and down the land, to beggar or lord, homeless wanderer or high born dame, he gladly gave unselfish service all unsought, and such as he helped straightway became his friends. To him who could bring her back to her father's castle should be given the throne and kingdom, as well as the Princess herself. So from far and near, indeed from almost every country under the sun, came knights and princes to fight the Ogre. Among those who drew back were Ethelried's brothers, the three that were dark and the three that were fair,. But Ethelried heeded not their taunts. So they all cried out long and loud Long live the Prince Prince Ciseaux."
from_code = "eng"
to_code = "deu"

# This chunk is characters-based, tokens can contain multiple, but keeping this as max ensures token max is never met
text_splitter = RecursiveCharacterTextSplitter(chunk_size=512)
text_splitted = text_splitter.split_text(text)
translated_chunks = []
for chunk in text_splitted:
    # Tokenize input
    inputs = tokenizer(chunk, return_tensors="pt", src_lang=from_code).to(device)
    # Generate translation
    with torch.no_grad():
        outputs = model.generate(**inputs, tgt_lang=to_code)

    # Decode translated text
    translated_text = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    translated_chunks.append(translated_text)

# Decode translated text
print(" ".join(translated_chunks))  # Translated sentence
