from entities.review import Review
from models.review import ReviewSchema
from flask import jsonify
from entities.databaseSessionManager import SessionManager
from entities.user import User
from models.user import UserSchema
from models.review import ReviewSchemaWithAuthorName
from entities.recipe import Recipe
from models.recipe import RecipeSchema

class ReviewCRUD():
    dbSession = SessionManager().session
    review_schemas = ReviewSchema(many=True)
    review_schema = ReviewSchema()
    user_schema = UserSchema()
    recipe_schemas = RecipeSchema(many=True)
    review_schemas_author = ReviewSchemaWithAuthorName(many=True)
    review_schema_author = ReviewSchemaWithAuthorName()

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
            if len(reviews) > 0:
                for review in reviews:
                    user = self.dbSession.query(User).filter_by(profileID=review.profileID).first()
                    if user:
                        review.Author = user.name
                    else:
                        review.Author = 'Unknown'
                message = 'Successfully detailed this review'
                results = self.review_schemas_author.dump(reviews)
                response = jsonify(results)
                response.message = message
                response.status = '200 OK'
                return response
            else:
                message = 'Successfully detailed this review'
                results = self.review_schemas.dump(reviews)
                response = jsonify(results)
                response.message = message
                response.status = '200 OK'
                return response
        else:
            message = 'There is no reviews for this id'
            return jsonify({'message':message,'success':'404 NOT FOUND'})
    def getReviewsByPaginationRecipeID(self,id,Page_Size,Page_Number_Per_Page):
        reviews = self.dbSession.query(Review).filter_by(RecipeID=id).all()
        if reviews :
            if len(reviews) > 0:
                offset = Page_Number_Per_Page * (Page_Size - 1)
                review_list_pagination =self.dbSession.query(Review).filter_by(RecipeID=id).order_by(Review.ReviewID.desc()).offset(offset).limit(Page_Number_Per_Page).all()
                for review in review_list_pagination:
                    user = self.dbSession.query(User).filter_by(profileID=review.profileID).first()
                    if user:
                        review.Author = user.name
                    else:
                        review.Author = 'Unknown'
                results = self.review_schemas_author.dump(review_list_pagination)
                message = 'Successfully detailed this review'
                response = jsonify(results)
                response.message = message
                response.status = '200 OK'
                return response
        else:
            message = 'There is no reviews for this id'
            return jsonify({'message':message,'success':'404 NOT FOUND'})

    def getReviewsByProfileID(self,id,Page_Size,Page_Number_Per_Page):
        offset = Page_Number_Per_Page * (Page_Size - 1)
        reviews =self.dbSession.query(Review).filter_by(profileID= id).order_by(Review.ReviewID.desc()).offset(offset).limit(Page_Number_Per_Page).all()
        total_reviews = self.dbSession.query(Review).filter_by(profileID= id).all()
        recipes_detail=[]
        recipe_list = []
        if reviews :
            for review in reviews:
                recipes_detail.append(self.dbSession.query(Recipe).filter_by(RecipeID=review.RecipeID).first())
            recipe_list = self.recipe_schemas.dump(recipes_detail)
            results = self.review_schemas.dump(reviews)
            data = {
                "reviews" : results,
                "total" : len(total_reviews),
                "recipes_detail":recipe_list
            }
            response = jsonify(data)
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
            message = 'Successfully added this review'
            response = self.review_schema.jsonify(review)
            response.message = message
            response.status = '200 OK'
            return response
        else:
            return jsonify({'message':error,'success':'500 INTERNAL ERROR'})
    
    def deleteReview(self,id): 
        review = self.dbSession.query(Review).get(id)
        if review :
            self.dbSession.delete(review)
            self.dbSession.commit()
            message = 'Successfully deleted this review'
            response = self.review_schema.jsonify(review)
            response.message = message
            response.status = '200 OK'
            return response
        else:
            message = 'There is no review yet'
            return jsonify({'message':message,'success':'404 NOT FOUND'})

    def editReview(self,id,RecipeID,profileID,Rate,Comments):
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