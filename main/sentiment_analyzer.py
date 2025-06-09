import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
import string
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud, STOPWORDS
import nltk

# Download necessary NLTK resources
nltk.download('vader_lexicon', quiet=True)
nltk.download('stopwords', quiet=True)

class SentimentAnalyzer:
    def __init__(self, data_path=None, text_column=None, rating_column=None, encoding='utf-8'):
        """
        Initialize the sentiment analyzer.
        
        Parameters:
        -----------
        data_path : str
            Path to the dataset file (CSV, Excel, etc.)
        text_column : str
            Name of the column containing review text
        rating_column : str
            Name of the column containing ratings (if available)
        encoding : str
            File encoding (default: 'utf-8')
        """
        self.data_path = data_path
        self.text_column = text_column
        self.rating_column = rating_column
        self.encoding = encoding
        self.stemmer = SnowballStemmer("english")
        self.stop_words = set(stopwords.words("english"))
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.data = None
        
    def load_data(self, data=None):
        """
        Load data from file or use provided DataFrame.
        
        Parameters:
        -----------
        data : pandas.DataFrame, optional
            DataFrame to use instead of loading from file
        
        Returns:
        --------
        pandas.DataFrame
            Loaded data
        """
        if data is not None:
            self.data = data
        elif self.data_path.endswith('.csv'):
            self.data = pd.read_csv(self.data_path, encoding=self.encoding)
        elif self.data_path.endswith(('.xls', '.xlsx')):
            self.data = pd.read_excel(self.data_path)
        elif self.data_path.endswith('.json'):
            self.data = pd.read_json(self.data_path)
        else:
            raise ValueError("Unsupported file format. Please provide CSV, Excel, or JSON file.")
        
        print(f"Data loaded successfully with {self.data.shape[0]} rows and {self.data.shape[1]} columns.")
        return self.data
    
    def clean_text(self, text):
        """
        Clean and preprocess text data.
        
        Parameters:
        -----------
        text : str
            Text to clean
        
        Returns:
        --------
        str
            Cleaned text
        """
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs, HTML tags, punctuation, and numbers
        text = re.sub(r"https?://\S+|www\.\S+", "", text)
        text = re.sub(r"<.*?>", "", text)
        text = re.sub(r"[%s]" % re.escape(string.punctuation), "", text)
        text = re.sub(r"\n", " ", text)
        text = re.sub(r"\w*\d\w*", "", text)
        
        # Remove stopwords and join
        words = [word for word in text.split() if word not in self.stop_words]
        text = " ".join(words)
        
        return text
    
    def preprocess_data(self):
        """
        Preprocess the data by cleaning text and preparing for analysis.
        
        Returns:
        --------
        pandas.DataFrame
            Preprocessed data
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        if self.text_column not in self.data.columns:
            raise ValueError(f"Text column '{self.text_column}' not found in data.")
        
        print("Preprocessing data...")
        self.data['cleaned_text'] = self.data[self.text_column].apply(self.clean_text)
        
        # Remove rows with empty text after cleaning
        self.data = self.data[self.data['cleaned_text'].str.strip() != ""]
        
        print(f"Preprocessing complete. {self.data.shape[0]} valid reviews remaining.")
        return self.data
    
    def analyze_sentiment(self):
        """
        Perform sentiment analysis on the preprocessed data.
        
        Returns:
        --------
        pandas.DataFrame
            Data with sentiment scores
        """
        if self.data is None or 'cleaned_text' not in self.data.columns:
            raise ValueError("Data not preprocessed. Call preprocess_data() first.")
        
        print("Analyzing sentiment...")
        
        # Calculate sentiment scores
        self.data["Positive"] = [self.sentiment_analyzer.polarity_scores(text)["pos"] for text in self.data['cleaned_text']]
        self.data["Negative"] = [self.sentiment_analyzer.polarity_scores(text)["neg"] for text in self.data['cleaned_text']]
        self.data["Neutral"] = [self.sentiment_analyzer.polarity_scores(text)["neu"] for text in self.data['cleaned_text']]
        self.data["Compound"] = [self.sentiment_analyzer.polarity_scores(text)["compound"] for text in self.data['cleaned_text']]
        
        # Categorize sentiment based on compound score
        self.data["Sentiment"] = self.data["Compound"].apply(
            lambda score: "Positive" if score >= 0.05 else ("Negative" if score <= -0.05 else "Neutral")
        )
        
        print("Sentiment analysis complete.")
        return self.data
    
    def cluster_data(self, n_clusters=3):
        """
        Perform K-means clustering on sentiment scores.
        
        Parameters:
        -----------
        n_clusters : int
            Number of clusters (default: 3)
        
        Returns:
        --------
        pandas.DataFrame
            Data with cluster assignments
        """
        if self.data is None or 'Positive' not in self.data.columns:
            raise ValueError("Sentiment analysis not performed. Call analyze_sentiment() first.")
        
        print(f"Clustering data into {n_clusters} groups...")
        
        # Prepare features for clustering
        X = self.data[['Positive', 'Negative', 'Neutral']]
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.data['Cluster'] = kmeans.fit_predict(X)
        
        # Analyze clusters
        cluster_centers = pd.DataFrame(
            kmeans.cluster_centers_, 
            columns=['Positive', 'Negative', 'Neutral']
        )
        
        # Label clusters based on dominant sentiment
        cluster_labels = []
        for i, center in cluster_centers.iterrows():
            if center['Positive'] > center['Negative'] and center['Positive'] > center['Neutral']:
                cluster_labels.append("Positive Cluster")
            elif center['Negative'] > center['Positive'] and center['Negative'] > center['Neutral']:
                cluster_labels.append("Negative Cluster")
            else:
                cluster_labels.append("Neutral Cluster")
        
        # Map cluster numbers to labels
        cluster_mapping = {i: label for i, label in enumerate(cluster_labels)}
        self.data['Cluster_Label'] = self.data['Cluster'].map(cluster_mapping)
        
        print("Clustering complete.")
        return self.data
    
    def extract_insights(self):
        """
        Extract actionable insights from the analyzed data.
        
        Returns:
        --------
        dict
            Dictionary containing insights
        """
        if self.data is None or 'Sentiment' not in self.data.columns:
            raise ValueError("Sentiment analysis not performed. Call analyze_sentiment() first.")
        
        print("Extracting insights...")
        
        insights = {
            'sentiment_distribution': self.data['Sentiment'].value_counts().to_dict(),
            'sentiment_percentages': (self.data['Sentiment'].value_counts(normalize=True) * 100).to_dict(),
            'average_scores': {
                'positive': self.data['Positive'].mean(),
                'negative': self.data['Negative'].mean(),
                'neutral': self.data['Neutral'].mean(),
                'compound': self.data['Compound'].mean()
            }
        }
        
        # Add rating insights if rating column exists
        if self.rating_column and self.rating_column in self.data.columns:
            insights['rating_distribution'] = self.data[self.rating_column].value_counts().to_dict()
            insights['average_rating'] = self.data[self.rating_column].mean()
            
            # Correlation between ratings and sentiment
            insights['rating_sentiment_correlation'] = {
                'positive': self.data[self.rating_column].corr(self.data['Positive']),
                'negative': self.data[self.rating_column].corr(self.data['Negative']),
                'compound': self.data[self.rating_column].corr(self.data['Compound'])
            }
            
            # Average sentiment by rating
            rating_sentiment = self.data.groupby(self.rating_column)['Compound'].mean().to_dict()
            insights['sentiment_by_rating'] = rating_sentiment
        
        print("Insights extracted successfully.")
        return insights
    
    def visualize_results(self, save_path=None):
        """
        Visualize the sentiment analysis results.
        
        Parameters:
        -----------
        save_path : str, optional
            Path to save visualizations
        """
        if self.data is None or 'Sentiment' not in self.data.columns:
            raise ValueError("Sentiment analysis not performed. Call analyze_sentiment() first.")
        
        print("Generating visualizations...")
        
        # Set up the style
        sns.set(style="whitegrid")
        plt.rcParams.update({'font.size': 12})
        
        # Create a figure for multiple plots
        fig = plt.figure(figsize=(20, 15))
        
        # 1. Sentiment Distribution - Pie Chart
        ax1 = fig.add_subplot(2, 3, 1)
        sentiment_counts = self.data['Sentiment'].value_counts()
        ax1.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', 
                startangle=90, colors=['green', 'red', 'gray'])
        ax1.set_title('Sentiment Distribution')
        
        # 2. Sentiment Scores - Bar Plot
        ax2 = fig.add_subplot(2, 3, 2)
        avg_scores = [self.data['Positive'].mean(), self.data['Negative'].mean(), self.data['Neutral'].mean()]
        ax2.bar(['Positive', 'Negative', 'Neutral'], avg_scores, color=['green', 'red', 'gray'])
        ax2.set_title('Average Sentiment Scores')
        ax2.set_ylabel('Score')
        
        # 3. Word Cloud
        ax3 = fig.add_subplot(2, 3, 3)
        text = " ".join(review for review in self.data['cleaned_text'])
        wordcloud = WordCloud(width=800, height=400, background_color='white', 
                             stopwords=STOPWORDS, max_words=100).generate(text)
        ax3.imshow(wordcloud, interpolation='bilinear')
        ax3.axis('off')
        ax3.set_title('Word Cloud of Reviews')
        
        # 4. Sentiment Distribution by Cluster
        if 'Cluster_Label' in self.data.columns:
            ax4 = fig.add_subplot(2, 3, 4)
            cluster_sentiment = pd.crosstab(self.data['Cluster_Label'], self.data['Sentiment'])
            cluster_sentiment.plot(kind='bar', stacked=True, ax=ax4, colormap='viridis')
            ax4.set_title('Sentiment Distribution by Cluster')
            ax4.set_xlabel('Cluster')
            ax4.set_ylabel('Count')
            ax4.legend(title='Sentiment')
        
        # 5. Rating vs Sentiment (if rating column exists)
        if self.rating_column and self.rating_column in self.data.columns:
            ax5 = fig.add_subplot(2, 3, 5)
            sns.boxplot(x=self.rating_column, y='Compound', data=self.data, ax=ax5)
            ax5.set_title('Rating vs Sentiment Score')
            ax5.set_xlabel('Rating')
            ax5.set_ylabel('Compound Sentiment Score')
        
        # 6. Sentiment Over Time (if timestamp column exists)
        timestamp_cols = [col for col in self.data.columns if any(time_word in col.lower() 
                                                                for time_word in ['date', 'time', 'timestamp'])]
        if timestamp_cols:
            try:
                time_col = timestamp_cols[0]
                self.data[time_col] = pd.to_datetime(self.data[time_col])
                self.data['month_year'] = self.data[time_col].dt.to_period('M')
                
                ax6 = fig.add_subplot(2, 3, 6)
                time_sentiment = self.data.groupby('month_year')['Compound'].mean()
                time_sentiment.plot(kind='line', marker='o', ax=ax6)
                ax6.set_title('Sentiment Trend Over Time')
                ax6.set_xlabel('Time Period')
                ax6.set_ylabel('Average Sentiment Score')
            except:
                # If time conversion fails, show cluster visualization instead
                if 'Cluster' in self.data.columns:
                    ax6 = fig.add_subplot(2, 3, 6)
                    sns.scatterplot(x='Positive', y='Negative', hue='Cluster_Label', data=self.data, ax=ax6)
                    ax6.set_title('Clusters by Sentiment Scores')
                    ax6.set_xlabel('Positive Score')
                    ax6.set_ylabel('Negative Score')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            print(f"Visualizations saved to {save_path}")
        
        plt.show()
        print("Visualizations complete.")
    
    def get_top_reviews(self, sentiment_type, n=5):
        """
        Get top reviews for a specific sentiment type.
        
        Parameters:
        -----------
        sentiment_type : str
            Type of sentiment ('Positive', 'Negative', or 'Neutral')
        n : int
            Number of reviews to return (default: 5)
        
        Returns:
        --------
        pandas.DataFrame
            Top reviews for the specified sentiment
        """
        if self.data is None or 'Sentiment' not in self.data.columns:
            raise ValueError("Sentiment analysis not performed. Call analyze_sentiment() first.")
        
        if sentiment_type not in ['Positive', 'Negative', 'Neutral']:
            raise ValueError("Invalid sentiment type. Choose from 'Positive', 'Negative', or 'Neutral'.")
        
        # Filter by sentiment and sort by compound score (absolute value for Neutral)
        if sentiment_type == 'Positive':
            filtered = self.data[self.data['Sentiment'] == sentiment_type].sort_values('Compound', ascending=False)
        elif sentiment_type == 'Negative':
            filtered = self.data[self.data['Sentiment'] == sentiment_type].sort_values('Compound', ascending=True)
        else:  # Neutral
            filtered = self.data[self.data['Sentiment'] == sentiment_type].copy()
            filtered['abs_compound'] = filtered['Compound'].abs()
            filtered = filtered.sort_values('abs_compound', ascending=True)
        
        # Select columns to display
        display_cols = [self.text_column]
        if self.rating_column and self.rating_column in self.data.columns:
            display_cols.append(self.rating_column)
        display_cols.extend(['Positive', 'Negative', 'Neutral', 'Compound'])
        
        return filtered[display_cols].head(n)
    
    def run_full_analysis(self, n_clusters=3, save_path=None):
        """
        Run the complete sentiment analysis pipeline.
        
        Parameters:
        -----------
        n_clusters : int
            Number of clusters for K-means (default: 3)
        save_path : str, optional
            Path to save visualizations
        
        Returns:
        --------
        tuple
            (processed_data, insights)
        """
        self.preprocess_data()
        self.analyze_sentiment()
        self.cluster_data(n_clusters=n_clusters)
        insights = self.extract_insights()
        self.visualize_results(save_path=save_path)
        
        return self.data, insights


# Example usage with the Flipkart dataset
def demo_flipkart_analysis():
    # For demonstration, we'll create a small sample dataset
    # In a real scenario, you would load your actual data file
    sample_data = pd.DataFrame({
        'Review': [
            "This product is amazing! I love it so much.",
            "Terrible quality, broke after one use. Waste of money.",
            "It's okay, nothing special but does the job.",
            "Best purchase I've made this year! Highly recommend.",
            "Disappointed with the product. Not as advertised."
        ],
        'Rate': [5, 1, 3, 5, 2]
    })
    
    # Initialize the analyzer
    analyzer = SentimentAnalyzer(text_column='Review', rating_column='Rate')
    
    # Load the sample data
    analyzer.load_data(data=sample_data)
    
    # Run the full analysis
    data, insights = analyzer.run_full_analysis()
    
    # Print insights
    print("\n=== SENTIMENT ANALYSIS INSIGHTS ===")
    print(f"Total reviews analyzed: {len(data)}")
    print(f"Sentiment distribution: {insights['sentiment_distribution']}")
    print(f"Sentiment percentages: {insights['sentiment_percentages']}")
    print(f"Average sentiment scores: {insights['average_scores']}")
    
    if 'rating_distribution' in insights:
        print(f"Rating distribution: {insights['rating_distribution']}")
        print(f"Average rating: {insights['average_rating']:.2f}")
        print(f"Correlation between rating and sentiment: {insights['rating_sentiment_correlation']}")
    
    # Show top positive and negative reviews
    print("\n=== TOP POSITIVE REVIEWS ===")
    print(analyzer.get_top_reviews('Positive', n=2))
    
    print("\n=== TOP NEGATIVE REVIEWS ===")
    print(analyzer.get_top_reviews('Negative', n=2))
    
    return analyzer

# Run the demo
analyzer = demo_flipkart_analysis()
