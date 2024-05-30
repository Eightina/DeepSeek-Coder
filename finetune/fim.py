import functools

import numpy as np


# this is expensive so we cache it
@functools.lru_cache(maxsize=None)
def get_fim_token_ids(tokenizer):
    # try:
    #     _, FIM_PREFIX, FIM_MIDDLE, FIM_SUFFIX, FIM_PAD = tokenizer.special_tokens_map[
    #         "additional_special_tokens"
    #     ][:5]
    #     suffix_tok_id, prefix_tok_id, middle_tok_id, pad_tok_id = (
    #         tokenizer.vocab[tok] for tok in [FIM_SUFFIX, FIM_PREFIX, FIM_MIDDLE, FIM_PAD]
    #     )
    # except KeyError:
    #     suffix_tok_id, prefix_tok_id, middle_tok_id, pad_tok_id = None, None, None, None
    # return suffix_tok_id, prefix_tok_id, middle_tok_id, pad_tok_id
    return tokenizer.added_tokens_encoder["<｜fim▁hole｜>"],\
            tokenizer.added_tokens_encoder["<｜fim▁begin｜>"],\
            tokenizer.added_tokens_encoder["<｜fim▁end｜>"]


## Adapted from https://github.com/bigcode-project/Megatron-LM/blob/6c4bf908df8fd86b4977f54bf5b8bd4b521003d1/megatron/data/gpt_dataset.py
def permute(
    sample,
    np_rng,
    suffix_tok_id,
    prefix_tok_id,
    middle_tok_id,
    # pad_tok_id,
    fim_rate=0.5,
    fim_spm_rate=0.5,
):
    """
    Take in a sample (list of tokens) and perform a FIM transformation on it with a probability of fim_rate, using two FIM modes:
    PSM and SPM (with a probability of fim_spm_rate).
    """

    if np_rng.binomial(1, fim_rate):
        boundaries = list(np_rng.randint(low=0, high=len(sample) + 1, size=2))
        boundaries.sort()

        prefix = np.array(sample[: boundaries[0]], dtype=np.int64)
        middle = np.array(sample[boundaries[0] : boundaries[1]], dtype=np.int64)
        suffix = np.array(sample[boundaries[1] :], dtype=np.int64)

        if np_rng.binomial(1, fim_spm_rate):
            # SPM (variant 2 from FIM paper)
            new_sample = np.concatenate(
                [
                    [prefix_tok_id, suffix_tok_id],
                    suffix,
                    [middle_tok_id],
                    prefix,
                    middle,
                ]
            )
        else:
            # PSM
            new_sample = np.concatenate(
                [
                    [prefix_tok_id],
                    prefix,
                    [suffix_tok_id],
                    suffix,
                    [middle_tok_id],
                    middle,
                ]
            )
    else:
        # don't do FIM preproc
        new_sample = sample

    return list(new_sample), np_rng
