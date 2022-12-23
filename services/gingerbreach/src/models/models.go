package models

type UserCreate struct {
	Username string `json:"username" binding:"required,alphanum,min=4,max=63"`
	Password string `json:"password" binding:"required,printascii,min=4,max=63"`
}

type UserLogin struct {
	Username string `json:"username" binding:"required,alphanum,min=4,max=63"`
	Password string `json:"password" binding:"required,printascii,min=4,max=63"`
}

type UserStorage struct {
	Username        string `json:"username" bson:"username"`
	Password        string `json:"password" bson:"password"`
	TangerinesEaten int64  `json:"tangerinesEaten" bson:"tangerines_eaten"`
}

type PublicUser struct {
	Username        string `json:"username"`
	TangerinesEaten int64  `json:"tangerinesEaten"`
}

type GetUser struct {
	Username string `json:"username" binding:"required,alphanum,min=4,max=63"`
}

type PostCreate struct {
	Text      string `json:"text" binding:"required,min=1"`
	IsPrivate *bool  `json:"isPrivate" binding:"required"`
}

type PostStorage struct {
	Id              string `json:"id" bson:"id"`
	Owner           string `json:"owner" bson:"owner"`
	Text            string `json:"text" bson:"text"`
	TangerinesEaten int64  `json:"tangerinesEaten" bson:"tangerines_eaten"`
	IsPrivate       *bool  `json:"isPrivate" bson:"is_private"`
}

type GetPost struct {
	Id string `json:"id" binding:"required"`
}
