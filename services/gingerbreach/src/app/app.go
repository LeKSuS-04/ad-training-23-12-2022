package app

import (
	"context"
	"fmt"
	"gingerbreach/storage"
	"math/rand"
	"os"
	"time"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.mongodb.org/mongo-driver/mongo/readpref"
)

type App struct {
	Mongo *mongo.Client
}

func (app *App) Init() {
	rand.Seed(time.Now().UnixNano())

	connectionUri := fmt.Sprintf("mongodb://%s:%s@mongo:27017", os.Getenv("MONGO_USER"), os.Getenv("MONGO_PASSWORD"))
	client, err := mongo.NewClient(options.Client().ApplyURI(connectionUri))
	if err != nil {
		panic(err)
	}

	err = client.Connect(context.TODO())
	if err != nil {
		panic(err)
	}

	err = client.Ping(context.TODO(), readpref.Primary())
	if err != nil {
		panic(err)
	}

	app.Mongo = client
	storage.InitIndexes(client)
}
