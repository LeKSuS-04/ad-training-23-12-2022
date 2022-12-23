package auth

import (
	"gingerbreach/models"
	"gingerbreach/storage"
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	"go.mongodb.org/mongo-driver/mongo"
)

func Authorization(client *mongo.Client) gin.HandlerFunc {
	return func(c *gin.Context) {
		defer c.Next()

		c.Set("user", nil)

		authorization := c.Request.Header.Get("Authorization")
		if authorization == "" {
			return
		}

		parts := strings.Split(authorization, " ")
		if len(parts) < 2 || parts[0] != "Basic" {
			return
		}

		creds := strings.Split(parts[1], ":")
		if len(creds) != 2 {
			return
		}

		username := creds[0]
		password := creds[1]
		user, err := storage.FindUser(client, username)
		if err != nil || user.Password != password {
			return
		}

		c.Set("user", user)
	}
}

func AuthRequired() gin.HandlerFunc {
	return func(c *gin.Context) {
		_, ok := c.MustGet("user").(models.UserStorage)
		if !ok {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
			c.Abort()
		} else {
			c.Next()
		}
	}
}
