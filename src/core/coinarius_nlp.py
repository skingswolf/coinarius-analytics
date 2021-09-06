from functools import reduce
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re
from scipy.stats import zscore
from sklearn.feature_extraction.text import TfidfVectorizer

# Following corpus downloads seem to be required
# for the packages `word_tokenize` function to work.
nltk.download("punkt")
nltk.download("stopwords")


class CoinariusNlp:
    """
    Represents a natural language processor that takes in as input text from articles
    about cryptocurrency news and outputs nlp analytics such as sentiment analysis and topic tags.
    """

    def __init__(self):
        """
        Initialises a new instance of this class.
        """

        self.__stopwords = set(stopwords.words("english"))
        for word in ["chart", "new", "data", "source", "total", "also"]:
            self.__stopwords.add(word)

        self.__tfidf_vectorizer = TfidfVectorizer(min_df=0.1, max_df=0.95)
        self.__stemmer = PorterStemmer()

        self.__positive_stemmed_sentiment_words = None
        self.__negative_stemmed_sentiment_words = None

    def initialise(self):
        """
        Initialises a new instance of this class.
        """

        positive_dict = pd.read_excel(
            "LoughranMcDonald_SentimentWordLists.xlsx",
            engine="openpyxl",
            sheet_name="Positive",
            header=None,
        )
        negative_dict = pd.read_excel(
            "LoughranMcDonald_SentimentWordLists.xlsx",
            engine="openpyxl",
            sheet_name="Negative",
            header=None,
        )

        self.__positive_stemmed_sentiment_words = self.__generate_stemmed_tokens(
            positive_dict[0].to_list()
        )
        self.__negative_stemmed_sentiment_words = self.__generate_stemmed_tokens(
            negative_dict[0].to_list()
        )

    def process(self, articles):
        """
        Parses and processes the given articles, outputting a dictionary which includes
        z-score, sentiment scores and topic tags.
        Parameters
        ----------
        Returns
        -------
            A dictionary which includes z-score, sentiment scores and topic tags.
        """

        # Preprocess documents
        document_token_matrix = {
            article["url"]: self.__generate_tokens(article["article_text"])
            for article in articles
        }
        stemmed_document_token_matrix = {
            article["url"]: self.__generate_stemmed_tokens(
                document_token_matrix[article["url"]]
            )
            for article in articles
        }
        tokenised_documents = [
            " ".join(tokenised_document)
            for tokenised_document in document_token_matrix.values()
        ]

        # Calculate tf-idf rankings for each unique token in the corpus.
        ranking = self.__generate_tfidf_ranking(
            self.__tfidf_vectorizer, tokenised_documents
        )

        # Calculate article sentiments
        urls = [article["url"] for article in articles]
        sentiment_scores = [
            self.__generate_sentiment_score(stemmed_document_token_matrix[url])
            for url in urls
        ]
        sentiment_zscores = zscore(sentiment_scores)
        article_sentiment = {}

        for idx in range(len(urls)):
            article_sentiment[urls[idx]] = {
                "sentiment_score": sentiment_scores[idx],
                "sentiment_z_score": sentiment_zscores[idx],
            }

        output = [
            {
                "url": article["url"],
                "title": article["title"],
                "date": article["date"],
                "z_score": article_sentiment[article["url"]]["sentiment_z_score"],
                "sentiment_score": article_sentiment[article["url"]]["sentiment_score"],
                "topics": self.__generate_topic_tags(
                    document_token_matrix[article["url"]], ranking
                ),
            }
            for article in articles
        ]

        return output

    def __generate_sentiment_score(self, stemmed_article_tokens):
        """
        Calculates a sentiment score associated with each article.
        Parameters
        ----------
        stemmed_article_tokens : str[]
            A list of stemmed tokens representing an article.
        """

        positive_score = 0
        negative_score = 0

        for token in stemmed_article_tokens:
            if token in self.__positive_stemmed_sentiment_words:
                positive_score += 1

            if token in self.__negative_stemmed_sentiment_words:
                negative_score += 1

        sentiment_score = (positive_score - negative_score) / (
            positive_score + negative_score
        )

        return sentiment_score

    def __generate_topic_tags(self, article_tokens, ranking):
        """
        Generates the 5 most popular topics associated with each article.
        Parameters
        ----------
        article_tokens : str[]
            A list of tokens representing an article.
        ranking : (token , score)[]
            A list of tuples containing a token (str) and it corresponding
            tfidf score over the entire collection of articles.
        Returns
        -------
            The 5 most popular topics associated with each article.
        """

        topics_tags = []
        num_topic_tags = 0
        max_num_topic_tags = 5

        # In descending order = first elements are the highest ranked.
        ranking_tokens = [tokens for (tokens, score) in ranking]

        for token in ranking_tokens:
            if num_topic_tags >= max_num_topic_tags:
                break

            if token in article_tokens:
                topics_tags.append(token)
                num_topic_tags += 1

        return topics_tags

    def __generate_tfidf_ranking(self, vectorizer, documents):
        """
        Parameters
        ----------
        vectorizer : TfidfVectorizer
            The tf-idf vectorizer.
        documents : str[]
            A list of strings each representing a document.
        Returns
        -------
            A list of tuples containing a token (str) and it corresponding
            tfidf score over the entire collection of articles.
        """

        document_term_matrix = self.__tfidf_vectorizer.fit_transform(documents)
        unique_terms = vectorizer.get_feature_names()

        document_term_matrix = document_term_matrix.toarray()
        num_documents = len(document_term_matrix)

        ranking = [
            (
                unique_terms[unique_term_idx],
                sum(
                    [
                        document_term_matrix[document_idx, unique_term_idx]
                        for document_idx in range(num_documents)
                    ]
                ),
            )
            for unique_term_idx in range(len(unique_terms))
        ]

        ranking.sort(key=lambda entry: entry[1], reverse=True)

        return ranking

    def __generate_tokens(self, article):
        """
        Tokenises the given article
        Parameters
        ----------
        article : str
            A string containing the article's text
        Returns
        -------
            A list of strings, i.e. tokens, representing the article.
        """

        raw_funcs = [self.__convert_to_lowercase, self.__remove_one_letter_words]
        formatted_article = reduce(lambda a, func: func(a), raw_funcs, article)

        token_funcs = [self.__clean_tokens, self.__remove_stopwords]
        article_tokens = reduce(lambda a, func: func(a), token_funcs, formatted_article)

        return article_tokens

    def __generate_stemmed_tokens(self, tokens):
        """
        Strips out any syntactic meaning in tokens such as tense.
        Parameters
        ----------
        tokens : str[]
        Returns
        -------
            A  list of stemmed tokens.
        """

        return [self.__stemmer.stem(token) for token in tokens]

    def __remove_stopwords(self, article_tokens):
        """
        Removes commonly used word in the English language from the tokens that
        carry very little information.
        Parameters
        ----------
        article_tokens : str[]
            The tokens for an article.
        Returns
        -------
            The article tokens minus any previously present stopwords.
        """

        # Takes only the words that are not in the stopwords set
        useful_words = [w for w in article_tokens if w not in self.__stopwords]
        return useful_words

    def __clean_tokens(self, article):
        """
        Tokenises the given article and removes any non-alphabetical symbols.
        Parameters
        ----------
        article : str
            A string representing the article text.
        Returns
        -------
            A list of tokens representing the original article.
        """

        # Uses the word_tokenize function to tokenize each 'row', i.e. minutes.
        tokens = nltk.word_tokenize(article)

        # Removes all non-alphabetic tokens.
        alpha_tokens = [w for w in tokens if w.isalpha()]
        return alpha_tokens

    def __convert_to_lowercase(self, article):
        """
        Converts all the text in the given article to lower case.
        Parameters
        ----------
        article : str
            A string representing the article text.
        Returns
        -------
            A lower case version of the given article.
        """

        return article.lower()

    def __remove_one_letter_words(self, article):
        """
        Removes one letter words such as I" from the article.
        Parameters
        ----------
        article : str
            A string representing the article text.
        Returns
        -------
            The article stripped of one letter words.
        """

        article = re.sub(r"\b[a-zA-Z]\b", "", article)

        return article
