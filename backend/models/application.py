class Application:
    def __init__(self, id, title, category, description, rating, icon_url, status, createdAt, updatedAt):
        self.id = id
        self.title = title
        self.category = category
        self.description = description
        self.rating = rating
        self.icon_url = icon_url
        self.status = status
        self.createdAt = createdAt
        self.updatedAt = updatedAt

    def to_dict(self):
        return self.__dict__