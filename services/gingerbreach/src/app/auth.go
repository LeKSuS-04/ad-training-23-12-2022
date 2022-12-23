package app

import (
	"gingerbreach/models"
	"gingerbreach/storage"
	"net/http"

	"github.com/gin-gonic/gin"
)

func (app *App) Me(c *gin.Context) {
	user, ok := c.MustGet("user").(models.UserStorage)
	if ok {
		c.JSON(http.StatusOK, gin.H{
			"user": user,
		})
	} else {
		c.JSON(http.StatusOK, gin.H{
			"message": "Unauthorized",
		})
	}
}

func (app *App) CreateUser(c *gin.Context) {
	var json models.UserCreate
	if err := c.ShouldBindJSON(&json); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	userToStorage := models.UserStorage{
		Username:        json.Username,
		Password:        json.Password,
		TangerinesEaten: 0,
	}

	if err := storage.CreateUser(app.Mongo, userToStorage); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
	}
}
