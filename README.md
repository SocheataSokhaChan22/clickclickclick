# clickclickclick URL Identifier
ClickClickClick URL Identifier is a tool developed by 3 junior students of the MIS department at Paragon International University.
Project Members: Morita Chhea, Socheata Sokhachan, Sophy Do

ClickClickClick URL Identifier detects phishing and malicious websites using a machine-learning algorithm. Machine learning algorithms can be used to detect phishing URLs by analyzing the characteristics of the URL, such as the domain name, the length of the URL, and the presence of certain keywords. Such algorithms can also detect similarities between phishing URLs and known phishing websites. 

# Approach
We used supervised learning to classify phishing and legitimate websites. We benefit from content-based approach and focus on html of the websites. Also, We used scikit-learn for the ML models. For this project, We created my own data set and defined features. We used requests library to collect data, BeautifulSoup module to parse and extract features. 

We used 4 different ML classifiers of scikit-learn and tested them implementing k-fold cross validation. Firstly obtained their confusion matrices, then calculated their accuracy, precision and recall scores. NB --> Gaussian Naive Bayes SVM --> Support Vector Machine DT --> Decision Tree RF --> Random Forest

As a result, the Random Forest model has the highest accuracy. ClickClickClick URL Identifier uses the Random Forest Model to detect phishing links.
