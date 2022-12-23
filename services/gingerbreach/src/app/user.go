package app

import (
	"encoding/json"
	"gingerbreach/models"
	"gingerbreach/storage"
	"io/ioutil"
	"math/rand"
	"net/http"

	"github.com/gin-gonic/gin"
)

var letters = []rune("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

func randId(length int) string {
	b := make([]rune, length)
	for i := range b {
		b[i] = letters[rand.Intn(len(letters))]
	}
	return string(b)
}

func (app *App) GetUser(c *gin.Context) {
	var json models.GetUser
	if err := c.ShouldBindJSON(&json); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	user, err := storage.FindUser(app.Mongo, json.Username)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	publicUser := models.PublicUser{
		Username:        user.Username,
		TangerinesEaten: user.TangerinesEaten,
	}
	c.JSON(http.StatusOK, gin.H{"user": publicUser})
}

func (app *App) EatTangerine(c *gin.Context) {
	user := c.MustGet("user").(models.UserStorage)
	err := storage.IncrementTangerineCount(app.Mongo, user.Username)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
	}
}

func (app *App) CreatePost(c *gin.Context) {
	user := c.MustGet("user").(models.UserStorage)
	var json models.PostCreate
	if err := c.ShouldBindJSON(&json); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	post := models.PostStorage{
		Id:              randId(24),
		Owner:           user.Username,
		Text:            json.Text,
		TangerinesEaten: user.TangerinesEaten,
		IsPrivate:       json.IsPrivate,
	}
	err := storage.CreatePost(app.Mongo, post)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
	}

	c.JSON(http.StatusOK, gin.H{"post": post})
}

func (app *App) GetPost(c *gin.Context) {
	var json models.GetPost
	if err := c.ShouldBindJSON(&json); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	post, err := storage.GetPostById(app.Mongo, json.Id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	user := c.MustGet("user").(models.UserStorage)
	if *post.IsPrivate && post.Owner != user.Username {
		c.JSON(http.StatusBadRequest, gin.H{"error": "This post isn't public"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"post": post})
}

func (app *App) GetUserPosts(c *gin.Context) {
	var json models.GetUser
	if err := c.ShouldBindJSON(&json); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	rules := make(map[string]interface{})
	rules["owner"] = json.Username
	posts, err := storage.SearchPublicPosts(app.Mongo, rules)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"posts": posts})
}

func (app *App) SearchPosts(c *gin.Context) {
	jsonDataBytes, err := ioutil.ReadAll(c.Request.Body)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	var query map[string]interface{}
	json.Unmarshal(jsonDataBytes, &query)
	posts, err := storage.SearchPublicPosts(app.Mongo, query)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"posts": posts})
}
