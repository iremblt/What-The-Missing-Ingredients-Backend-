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
        if len(review_list) == 0 :
            message = 'There is no reviews yet. You can add a new comments'
            return jsonify({'message':message,'success':'404 NOT FOUND'})
        else:
            message = 'Successfully listed all reviews'
            results = self.review_schemas.dump(review_list)
            response = jsonify(results)
            response.message = message
            response.status = '200 OK'
            return response
    
    def getReviewsByRecipeID(self,id):
        reviews = self.dbSession.query(Review).filter_by(RecipeID=id).all()
        if reviews :
            message = 'Successfully detailed this review'
            results = self.review_schemas.dump(reviews)
            response = jsonify(results)
            response.message = message
            response.status = '200 OK'
            return response
        else:
            message = 'There is no reviews for this id'
            return jsonify({'message':message,'success':'404 NOT FOUND'})

    def getReviewsByProfileID(self,id):
        reviews = self.dbSession.query(Review).filter_by(profileID=id).all()
        if reviews :
            message = 'Successfully detailed this review'
            results = self.review_schemas.dump(reviews)
            response = jsonify(results)
            response.message = message
            response.status = '200 OK'
            return response
        else:
            message = 'You did not review yet'
            return jsonify({'message':message,'success':'404 NOT FOUND'})

    def addReview(self,RecipeID,profileID,Rate,Comments):
        error = self.validateReview(Rate)
        if error is 'None':
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
            message = 'Successfully added this recipe'
            response = self.review_schema.jsonify(review)
            response.message = message
            response.status = '200 OK'
            return response
        else:
            return jsonify({'message':error,'success':'500 INTERNAL ERROR'})
    
    def deleteReview(self,id): 
        reviews_list = pd.read_csv('clean_reviews.csv')
        review = self.dbSession.query(Review).get(id)
        if review :
            self.dbSession.delete(review)
            self.dbSession.commit()
            reviews_list = reviews_list.drop(reviews_list[(reviews_list['ReviewID'] == int(id))].index)
            reviews_list.to_csv('clean_reviews.csv', index=False)
            message = 'Successfully deleted this review'
            response = self.review_schema.jsonify(review)
            response.message = message
            response.status = '200 OK'
            return response
        else:
            message = 'There is no review yet'
            return jsonify({'message':message,'success':'404 NOT FOUND'})

    def editReview(self,id,RecipeID,profileID,Rate,Comments):
        reviews_list = pd.read_csv('clean_reviews.csv')
        error = self.validateReview(Rate)
        if error is 'None':
            review = self.dbSession.query(Review).get(id)
            if review is None:
                return  jsonify({'message':'There is no review this id','success':'404 NOT FOUND'})
            else:
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

                message = 'Successfully added this review'
                response = self.review_schema.jsonify(review)
                response.message = message
                response.status = '200 OK'
                return response
        else:
            return jsonify({'message':error,'success':'500 INTERNAL ERROR'})

    def validateReview(self,Rate):
        error = 'None'
        if not Rate:
            error = 'Rate is required.'
        return error