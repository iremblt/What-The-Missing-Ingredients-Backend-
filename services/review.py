from entities.review import Review
from models.review import ReviewSchema
from flask import jsonify
import pandas as pd
from entities.databaseSessionManager import SessionManager

class ReviewCRUD():
    dbSession = SessionManager().session
    review_schemas = ReviewSchema(many=True)
    review_schema = ReviewSchema()

    def getReviewList(self):
        review_list = self.dbSession.query(Review).all()
        results = self.review_schemas.dump(review_list)
        return jsonify(results)
    
    def getReviewsByRecipeID(self,id):
        reviews = self.dbSession.query(Review).filter_by(RecipeID=id).all()
        return self.review_schemas.dump(reviews)

    def getReviewsByProfileID(self,id):
        reviews = self.dbSession.query(Review).filter_by(profileID=id).all()
        return self.review_schemas.dump(reviews)

    def addReview(self,RecipeID,profileID,Rate,Comments):
        review = Review(RecipeID, profileID, Rate, Comments)
        self.dbSession.add(review)
        self.dbSession.commit()
        ReviewID = review.ReviewID
        reviewCSV = {
        'RecipeID': [RecipeID],
        'profileID': [profileID],
        'Rate': [Rate],
        'ReviewID': [ReviewID],
        'Comments':[Comments]
        }
        df = pd.DataFrame(reviewCSV)
        df.to_csv('clean_reviews.csv', mode='a', index=False, header=False)        
        return self.review_schema.jsonify(review)
    
    
    def deleteReview(self,id): 
        reviews_list = pd.read_csv('clean_reviews.csv')
        review = self.dbSession.query(Review).get(id)
        self.dbSession.delete(review)
        self.dbSession.commit()
        reviews_list = reviews_list.drop(reviews_list[(reviews_list['ReviewID'] == int(id))].index)
        reviews_list.to_csv('clean_reviews.csv', index=False)
        return self.review_schema.jsonify(review)
    
    def editReview(self,id,RecipeID,profileID,Rate,Comments):
        reviews_list = pd.read_csv('clean_reviews.csv')
        review = self.dbSession.query(Review).get(id) 
        review.RecipeID = RecipeID
        review.profileID = profileID
        review.Rate = Rate
        review.Comments = Comments
        self.dbSession.commit()
        
        index = reviews_list.index[reviews_list['ReviewID'] == int(id)].tolist()
        reviews_list.loc[index[0], 'RecipeID'] = RecipeID
        reviews_list.loc[index[0], 'profileID'] = profileID
        reviews_list.loc[index[0], 'Rate'] = Rate
        reviews_list.loc[index[0], 'Comments'] = Comments
        reviews_list.to_csv('clean_reviews.csv', index=False)

        return self.review_schema.jsonify(review)