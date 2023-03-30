
CREATE TABLE users
(
   id                      INTEGER PRIMARY KEY,
   username                VARCHAR        NOT NULL,
   email                   VARCHAR        NOT NULL,
   password                VARCHAR        NOT NULL,
   coins                   INTEGER        NOT NULL,
   selected_grid_skin      VARCHAR        NOT NULL,
   selected_pieces_skin    VARCHAR        NOT NULL,
   elo                     INTEGER        NOT NULL,
   profile_picture         VARCHAR        ,
   is_banned               BOOLEAN        NOT NULL
);

CREATE TABLE tableros
(
   id                   INTEGER PRIMARY KEY,
   board_distribution   VARCHAR        NOT NULL
);

CREATE TABLE board_skins
(
   id            INTEGER PRIMARY KEY,
   name          VARCHAR        NOT NULL,
   description   VARCHAR        NOT NULL,
   image         VARCHAR        NOT NULL,
   price        INTEGER        NOT NULL
);

CREATE TABLE piece_skins
(
   id            INTEGER PRIMARY KEY,
   name          VARCHAR        NOT NULL,
   image         VARCHAR        NOT NULL,
   description   VARCHAR        NOT NULL,
   price        INTEGER        NOT NULL
);

CREATE TABLE befriends
(
   request_status   BOOLEAN        NOT NULL,
   user_id          INTEGER,
   friend_id        INTEGER,
   PRIMARY KEY (user_id,friend_id),
   FOREIGN KEY (user_id) REFERENCES users(id),
   FOREIGN KEY (friend_id) REFERENCES users(id)
);

CREATE TABLE has_board_skins
(
   user_id         INTEGER,
   board_skin_id   INTEGER,
   PRIMARY KEY (user_id,board_skin_id),
   FOREIGN KEY (user_id) REFERENCES users(id),
   FOREIGN KEY (board_skin_id) REFERENCES board_skins(id)
);

CREATE TABLE has_piece_skins
(
   user_id         INTEGER,
   piece_skin_id   INTEGER,
   PRIMARY KEY (user_id,piece_skin_id),
   FOREIGN KEY (user_id) REFERENCES users(id),
   FOREIGN KEY (piece_skin_id) REFERENCES piece_skins(id)
);
