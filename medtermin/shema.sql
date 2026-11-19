CREATE TABLE korisnici (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email         TEXT,
    ime           TEXT,
    prezime       TEXT,
    uloga         TEXT NOT NULL,
    oib           TEXT
);

CREATE TABLE reset_tokeni (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT    NOT NULL,
    token      TEXT    NOT NULL,
    istjece    TEXT,
    iskoristen INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE postavke (
    username   TEXT PRIMARY KEY,
    podsjetnik INTEGER NOT NULL,
    sati_prije INTEGER NOT NULL,
    kanal      TEXT    NOT NULL
);

CREATE TABLE lijecnici (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ime             TEXT NOT NULL,
    prezime         TEXT NOT NULL,
    specijalizacija TEXT NOT NULL,
    ordinacija      TEXT NOT NULL
);

CREATE TABLE termini (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    lijecnik_id INTEGER NOT NULL REFERENCES lijecnici (id),
    pocetak     TEXT    NOT NULL,
    kapacitet   INTEGER NOT NULL,
    zauzeto     INTEGER NOT NULL DEFAULT 0,
    napomena    TEXT
);

CREATE TABLE rezervacije (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    termin_id  INTEGER NOT NULL REFERENCES termini (id),
    pacijent   TEXT    NOT NULL,
    napomena   TEXT,
    oib        TEXT,
    kreirano   TEXT    NOT NULL,
    oznaka_bis TEXT
);

CREATE TABLE nalazi (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    pacijent TEXT NOT NULL,
    naziv    TEXT NOT NULL,
    datoteka TEXT NOT NULL
);
