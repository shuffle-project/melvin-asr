import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer


def merge_subwords(tokens):
    """Merge subwords back into full words."""
    words = []
    current_word = ""
    for token in tokens:
        if token.startswith("##"):
            current_word += token[2:]  # Append subword without ##
        else:
            if current_word:
                words.append(current_word)
            current_word = token
    if current_word:
        words.append(current_word)
    return words


# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
model = AutoModel.from_pretrained(
    "bert-base-multilingual-cased", output_attentions=True
)

# Define sentences
source_sentence = "I am trying to understand how this works"
target_sentence = "Ich versuche zu verstehen wie das hier funktioniert"

# Tokenize inputs
inputs = tokenizer(
    source_sentence,
    target_sentence,
    return_tensors="pt",
    truncation=True,
    padding=True,
    return_token_type_ids=True,
)

# Get attention outputs
with torch.no_grad():
    outputs = model(**inputs)

# Get attention scores from the last layer
attention_weights = outputs.attentions[-1]
attention_matrix = attention_weights.mean(dim=1).squeeze(0)

# Convert tokens to words
input_ids = inputs["input_ids"].squeeze(0)
tokens = tokenizer.convert_ids_to_tokens(input_ids)
sep_index = tokens.index("[SEP]")
source_tokens = tokens[1:sep_index]  # Exclude CLS and SEP
target_tokens = tokens[sep_index + 1 : -1]  # Exclude SEP

# Merge subwords into full words
source_words = merge_subwords(source_tokens)
target_words = merge_subwords(target_tokens)

# Compute alignment scores for word-level tokens
alignment_scores = attention_matrix[1:sep_index, sep_index + 1 : -1].cpu().numpy()

# Map subwords back to word indices
source_indices = []
for i, token in enumerate(source_tokens):
    if not token.startswith("##"):
        source_indices.append(i)

target_indices = []
for i, token in enumerate(target_tokens):
    if not token.startswith("##"):
        target_indices.append(i)

# Aggregate alignment scores for word-level tokens
word_alignment_scores = alignment_scores[np.ix_(source_indices, target_indices)]

# Find the best alignments for each source word
alignments = {}
aligned_target_indices = set()  # Track which target words have been aligned

for src_idx, src_word in enumerate(source_words):
    tgt_idx = word_alignment_scores[src_idx].argmax()  # Target word with max score
    alignments[src_word] = target_words[tgt_idx]
    aligned_target_indices.add(tgt_idx)  # Mark this target word as aligned

# Add missing target words
unaligned_target_indices = [
    i for i in range(len(target_words)) if i not in aligned_target_indices
]

# Map unaligned target words
for tgt_idx in unaligned_target_indices:
    alignments[f"[extra_{tgt_idx}]"] = target_words[tgt_idx]

# Print word-level alignments
print("Word-level alignments:", alignments)
