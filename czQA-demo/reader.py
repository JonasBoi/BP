import torch
from transformers import BertTokenizerFast, BertForQuestionAnswering
import numpy as np


class Reader:

    def __init__(self, model_checkpoint, max_answer_length=10, n_best_size=10, max_length=384, stride=128,
                 use_cpu=False):
        # load all parameters of the reader
        self.max_answer_length = max_answer_length  # max answer span length
        self.n_best_size = n_best_size  #
        self.max_length = max_length  # max count of tokens in one tokenized passage
        self.stride = stride  # the length of overlap between two mini-batches of tokenizer

        # choose device; cuda if available
        self.device = torch.device("cuda:0" if (torch.cuda.is_available() and use_cpu is False) else "cpu")

        # load tokenizer and model from pretrained checkpoint
        self.tokenizer = BertTokenizerFast.from_pretrained(model_checkpoint)
        # load model to device if possible
        self.model = BertForQuestionAnswering.from_pretrained(model_checkpoint).to(self.device)

        print("Model loaded from: " + model_checkpoint)
        print("Device selected:")
        print(self.device)

    def decode(self, output, context, offset_mappings):
        """
        get the text span from the span scores

        method has been partly borrowed from
        https://colab.research.google.com/github/huggingface/notebooks/blob/master/examples/question_answering.ipynb

        its also thoroughly commented there
        """
        # enumerate over all outputs (max output size is 500 tokens in a log prob tensor)
        valid_answers = []

        for i, _ in enumerate(output.start_logits):

            start_logits = output.start_logits[i].cpu().detach().numpy()
            end_logits = output.end_logits[i].cpu().detach().numpy()
            offset_mapping = offset_mappings[i]

            # Gather the indices the best start/end logits:
            start_indexes = np.argsort(start_logits)[-1: - self.n_best_size - 1: -1].tolist()
            end_indexes = np.argsort(end_logits)[-1: - self.n_best_size - 1: -1].tolist()
            for start_index in start_indexes:
                for end_index in end_indexes:
                    # Don't consider out-of-scope answers, either because the indices are out of bounds or correspond
                    # to part of the input_ids that are not in the context.
                    if (
                            start_index >= len(offset_mapping)
                            or end_index >= len(offset_mapping)
                            or offset_mapping[start_index] is None
                            or offset_mapping[end_index] is None
                    ):
                        continue
                    # Don't consider answers with a length that is either < 0 or > max_answer_length.
                    if end_index < start_index or end_index - start_index + 1 > self.max_answer_length:
                        continue
                    # We need to refine that test to check the answer is inside the context
                    if start_index <= end_index:
                        start_char = offset_mapping[start_index][0]
                        end_char = offset_mapping[end_index][1]
                        valid_answers.append(
                            {
                                "score": start_logits[start_index] + end_logits[end_index],
                                "text": context[start_char: end_char].strip()
                            }
                        )
        valid_answers = sorted(valid_answers, key=lambda x: x["score"], reverse=True)[:self.n_best_size]
        return valid_answers

    def get_answers(self, question, context):
        """
        get the best answers from the context to the question

        """
        # tokenize the input for the model using special huggingface tokenizer
        inputs = self.tokenizer(question, context,
                                return_tensors='pt',
                                truncation="only_second",
                                max_length=self.max_length,  # to prevent cuda running out of memory
                                stride=self.stride,  # overlap within splitted long
                                return_offsets_mapping=True,
                                return_overflowing_tokens=True,
                                padding="max_length")
        inputs.to(self.device)  # port inputs to gpu

        # get the model predictions
        outputs = self.model(inputs['input_ids'],
                             token_type_ids=inputs['token_type_ids'],
                             attention_mask=inputs['attention_mask'])

        # use the decode function to get the n_best_size best valid answers
        valid_answers = self.decode(outputs, context, inputs['offset_mapping'])

        return valid_answers
