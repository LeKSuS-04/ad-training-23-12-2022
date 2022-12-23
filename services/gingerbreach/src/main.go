package main

import (
	"gingerbreach/app"
	"gingerbreach/auth"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	app := app.App{}
	app.Init()

	r.Use(auth.Authorization(app.Mongo))

	authorization := r.Group("/auth")
	{
		authorization.GET("/me", app.Me)
		authorization.POST("/create", app.CreateUser)
	}

	authorized := r.Group("/")
	authorized.Use(auth.AuthRequired())
	{
		authorized.GET("/get_user", app.GetUser)
		authorized.POST("/eat_tangerine", app.EatTangerine)
		authorized.POST("/create_post", app.CreatePost)
		authorized.GET("/get_post", app.GetPost)
		authorized.GET("/get_user_posts", app.GetUserPosts)
		authorized.GET("/search_posts", app.SearchPosts)
	}

	r.Run()
}
