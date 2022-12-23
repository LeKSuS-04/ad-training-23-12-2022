package storage

import (
	"context"
	"gingerbreach/models"
	"log"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func InitIndexes(client *mongo.Client) {
	usersCollection := client.Database("storage").Collection("users")
	indexModel := mongo.IndexModel{
		Keys:    bson.D{{Key: "username", Value: 1}},
		Options: options.Index().SetUnique(true),
	}
	_, err := usersCollection.Indexes().CreateOne(context.Background(), indexModel)
	if err != nil {
		log.Fatalf("Unable to create unique index: %v", err)
	}

	postsCollection := client.Database("storage").Collection("posts")
	indexModel = mongo.IndexModel{
		Keys: bson.D{{Key: "owner", Value: 1}},
	}
	_, err = postsCollection.Indexes().CreateOne(context.Background(), indexModel)
	if err != nil {
		log.Fatalf("Unable to create index: %v", err)
	}
	indexModel = mongo.IndexModel{
		Keys:    bson.D{{Key: "id", Value: 1}},
		Options: options.Index().SetUnique(true),
	}
	_, err = postsCollection.Indexes().CreateOne(context.Background(), indexModel)
	if err != nil {
		log.Fatalf("Unable to create unique index: %v", err)
	}
}

func FindUser(client *mongo.Client, username string) (models.UserStorage, error) {
	collection := client.Database("storage").Collection("users")
	filter := bson.M{
		"username": username,
	}
	var user models.UserStorage
	err := collection.FindOne(context.Background(), filter).Decode(&user)
	return user, err
}

func CreateUser(client *mongo.Client, user models.UserStorage) error {
	collection := client.Database("storage").Collection("users")
	_, err := collection.InsertOne(context.Background(), user)
	return err
}

func IncrementTangerineCount(client *mongo.Client, username string) error {
	collection := client.Database("storage").Collection("users")
	filter := bson.M{
		"username": username,
	}
	update := bson.D{{
		Key: "$inc",
		Value: bson.D{{
			Key:   "tangerines_eaten",
			Value: 1,
		}},
	}}
	_, err := collection.UpdateOne(context.Background(), filter, update)
	return err
}

func CreatePost(client *mongo.Client, post models.PostStorage) error {
	collection := client.Database("storage").Collection("posts")
	_, err := collection.InsertOne(context.Background(), post)
	return err
}

func GetPostById(client *mongo.Client, id string) (models.PostStorage, error) {
	collection := client.Database("storage").Collection("posts")
	filter := bson.M{
		"id": id,
	}
	var post models.PostStorage
	err := collection.FindOne(context.Background(), filter).Decode(&post)
	return post, err
}

func SearchPublicPosts(client *mongo.Client, rules map[string]interface{}) (result []string, err error) {
	collection := client.Database("storage").Collection("posts")
	filter := bson.M{
		"is_private": false,
	}
	for k, v := range rules {
		filter[k] = v
	}
	cur, err := collection.Find(context.Background(), filter, options.Find())
	if err != nil {
		return nil, err
	}

	for cur.Next(context.Background()) {
		var nextPost models.PostStorage
		err := cur.Decode(&nextPost)
		if err != nil {
			return nil, err
		}
		result = append(result, nextPost.Id)
	}
	return result, nil
}
