# This file handles the updated chunking logic. The logic is generally as follows (flow chart created by ChatGPT):
# NOTE: currently the chunking logic is set for punctuated Classical Chinese texts.
# TODO: Add a system to account for unpunctuated texts differently? / Analyze how it interacts with unpunctuated texts now. (It think it might work now)
#                 ┌───────────────────────────┐
#                 │  Read input file (lines)  │
#                 └─────────────┬─────────────┘
#                               │
#                               ▼
#                    ┌──────────────────────┐
#                    │ For each line in text│
#                    └─────────────┬────────┘
#                                  │
#                   ┌──────────────┴──────────────┐
#                   ▼                             ▼
#       ┌─────────────────────────┐    ┌─────────────────────────┐
#       │ Check if paragraph?     │    │ Not a paragraph →       │
#       │ (≥ MIN size & ≥ 2 punc) │    │ keep as single chunk    │
#       └─────────────┬───────────┘    └─────────────────────────┘
#                     │
#       ┌─────────────┴───────────────┐
#       ▼                             ▼
# ┌────────────────────┐     ┌───────────────────────────────┐
# │ Length ≤ MAX size? │     │ Length > MAX size → Split     │
# │ Keep as one chunk  │     │ (find midpoint + nearest punc)│
# └────────────────────┘     └───────────────────────────────┘
#                                   │
#                                   ▼
#                    ┌─────────────────────────────┐
#                    │ Recursively split if needed │
#                    └─────────────────────────────┘

# ----------------------------------------------------------

#           After first pass → Have initial list of chunks

# ----------------------------------------------------------

#                 ┌───────────────────────────┐
#                 │ Second pass (bottom-up): │
#                 │ Merge adjacent chunks if │
#                 │ combined ≤ MAX_CHUNK_SIZE│
#                 └─────────────┬─────────────┘
#                               │
#                               ▼
#                 ┌───────────────────────────┐
#                 │ Save chunks to output file│
#                 │ + delimiter "-----CHUNK---│
#                 └───────────────────────────┘

from collections import deque

# hyperparameters to tune
PARAGRAPH_SIZE = 384 # in my test text covers 94% of paragraphs
MIN_CHUNK_SIZE = 128
MAX_CHUNK_SIZE = PARAGRAPH_SIZE # Currently set to be the same as PARAGRAPH_SIZE but could be adjusted separately.

# any paragraph longer than PARAGRAPH_SIZE will be split into equal smaller chunks with smart chunking
PUNCTUATION = ['。', '!', '?'] #recognized punctuation for sentence ending.


# identify paragraphs. Paragraphs have the following characteristics:
    # 1. On a single line
    # 2. have at least two PUNCTUATION sentence ending characters
    # 3. Of a length of at least MIN_CHUNK_SIZE
def find_paragraph(line): # 
    if len(line) >= MIN_CHUNK_SIZE:
        sentence_count = sum(line.count(p) for p in PUNCTUATION)
        if sentence_count >= 2:
            # we have found a paragraph!
            return True
    return False

# logic for splitting paragraphs which are longer than PARAGRAPH_SIZE
    # 1. Find length of the paragraph and divide by 2 to get the mid point
    # 2. Look for the nearest punctuation to the mid point (either direction)
    # 3. Split the paragraph at that punctuation
def split_paragraph(paragraph):
    if len(paragraph) <= PARAGRAPH_SIZE:
        return [paragraph]

    mid_point = len(paragraph) // 2
    split_index = -1

    # Search for nearest punctuation to the left
    for i in range(mid_point, -1, -1):
        if paragraph[i] in PUNCTUATION:
            if i + 1 >= MIN_CHUNK_SIZE and (len(paragraph) - (i + 1)) >= MIN_CHUNK_SIZE:
                split_index = i + 1
                break
    # If not found, search to the right
    if split_index == -1:
        for i in range(mid_point, len(paragraph)):
            if paragraph[i] in PUNCTUATION:
                if i + 1 >= MIN_CHUNK_SIZE and (len(paragraph) - (i + 1)) >= MIN_CHUNK_SIZE:
                    split_index = i + 1
                    break
    # If no valid split point, just return whole paragraph
    if split_index == -1:
        print("sketchy split!")
        return [paragraph]
    
    left = paragraph[:split_index]
    right = paragraph[split_index:]
    return split_paragraph(left) + split_paragraph(right)

def chunk_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        chunks = content.split('\n')

        new_chunks = []
        for line in chunks:
            if find_paragraph(line):
                # split_paragraph may return 1 or many pieces
                new_chunks.extend(split_paragraph(line))
            else:
                new_chunks.append(line)

        chunks = new_chunks
        # First pass processing complete! Split the paragraphs correctly

        # Second pass: Finalize the chunks by merging smaller chunks as necessary.
            # 1. From the bottom up, if merging the current chunk with the previous chunk does not exceed MAX_CHUNK_SIZE, do so.
            # 2. Continue until all chunks are processed.
        finalized_chunks = deque()
        for chunk in reversed(chunks):
            if finalized_chunks and len(chunk) + len(finalized_chunks[0]) <= MAX_CHUNK_SIZE:
                # Preserve the newline between merged chunks, keeps the formatting consistent.
                merged_chunk = chunk + '\n' + finalized_chunks.popleft()
                finalized_chunks.appendleft(merged_chunk)
            else:
                finalized_chunks.appendleft(chunk)
        # # Save finalized chunks to a new file (can be used to check chunk sizes)
        # with open('finalized_chunks.txt', 'w', encoding='utf-8') as finalfile:
        #     for i, chunk in enumerate(finalized_chunks):
        #         # finalfile.write(chunk + '\n')
        #         # write delimiter between chunks (not after the last chunk)
        #         if i != len(finalized_chunks) - 1:
        #             finalfile.write(f"-----CHUNK----- ({len(chunk)} chars)\n")
    return finalized_chunks


# if __name__ == "__main__":    
#     print("Chunking file in chunking.py:", FILEPATH)
#     chunk_file(FILEPATH)