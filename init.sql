-- ============================================
-- Инициализация базы данных Movie Tracker
-- Автоматически выполняется при первом запуске PostgreSQL
-- ============================================


-- ============================================
-- Таблица пользователей (Telegram)
-- ============================================
--telegram_id был поменян на VARCHAR вместо INT
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id VARCHAR(50) UNIQUE NOT NULL, 
    username VARCHAR(255) UNIQUE,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Индексы для таблицы users
CREATE INDEX IF NOT EXISTS idx_users_id ON users(id);
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- ============================================
-- Таблица категорий контента
-- ============================================
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    
    -- Индексы
    CONSTRAINT unique_category_name UNIQUE (name)
);

-- Индексы для таблицы categories
CREATE INDEX IF NOT EXISTS idx_categories_id ON categories(id);
CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);

-- ============================================
-- Таблица контента (фильмы и сериалы)
-- ============================================
CREATE TABLE IF NOT EXISTS content (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    original_title VARCHAR(255),
    description TEXT,
    content_type VARCHAR(50) NOT NULL,  -- 'movie' или 'series'
    release_year INTEGER,
    duration_minutes INTEGER,  -- для фильмов
    total_seasons INTEGER,     -- для сериалов
    total_episodes INTEGER,    -- для сериалов
    imdb_rating DOUBLE PRECISION,
    imdb_id VARCHAR(20) UNIQUE,
    poster_url VARCHAR(500),
    genre VARCHAR(255),
    director VARCHAR(255),
    actors_cast TEXT,
    language VARCHAR(100),
    country VARCHAR(100),
    
    -- Внешний ключ на категорию
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    
    -- Технические поля
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Индексы для таблицы content
CREATE INDEX IF NOT EXISTS idx_content_id ON content(id);
CREATE INDEX IF NOT EXISTS idx_content_title ON content(title);
CREATE INDEX IF NOT EXISTS idx_content_content_type ON content(content_type);
CREATE INDEX IF NOT EXISTS idx_content_release_year ON content(release_year);
CREATE INDEX IF NOT EXISTS idx_content_imdb_rating ON content(imdb_rating);
CREATE INDEX IF NOT EXISTS idx_content_category_id ON content(category_id);
CREATE INDEX IF NOT EXISTS idx_content_is_active ON content(is_active);

-- Проверка для content_type
ALTER TABLE content ADD CONSTRAINT check_content_type 
    CHECK (content_type IN ('movie', 'series'));

-- ============================================
-- Таблица истории просмотров
-- ============================================
CREATE TABLE IF NOT EXISTS view_history (
    id SERIAL PRIMARY KEY,
    
    -- Внешние ключи
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_id INTEGER NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    
    -- Детали просмотра
    watched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    rating DOUBLE PRECISION CHECK (rating >= 1 AND rating <= 10),
    season INTEGER,         -- для сериалов
    episode INTEGER,        -- для сериалов
    episode_title VARCHAR(255),  -- для сериалов
    duration_watched INTEGER,    -- в минутах
    rewatch BOOLEAN DEFAULT FALSE,
    notes TEXT,
    
    -- Технические поля
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Индексы для таблицы view_history
CREATE INDEX IF NOT EXISTS idx_view_history_id ON view_history(id);
CREATE INDEX IF NOT EXISTS idx_view_history_user_id ON view_history(user_id);
CREATE INDEX IF NOT EXISTS idx_view_history_content_id ON view_history(content_id);
CREATE INDEX IF NOT EXISTS idx_view_history_watched_at ON view_history(watched_at);
CREATE INDEX IF NOT EXISTS idx_view_history_user_content ON view_history(user_id, content_id);

-- Уникальность комбинации user_id + content_id + watched_at (чтобы избежать дублей)
ALTER TABLE view_history ADD CONSTRAINT unique_view_record 
    UNIQUE (user_id, content_id, watched_at);

-- ============================================
-- Таблица списка ожидания (watchlist)
-- ============================================
CREATE TABLE IF NOT EXISTS watchlist (
    id SERIAL PRIMARY KEY,
    
    -- Внешние ключи
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_id INTEGER NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    
    -- Детали
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    priority INTEGER DEFAULT 1 CHECK (priority >= 1 AND priority <= 5),
    notes TEXT
);

-- Индексы для таблицы watchlist
CREATE INDEX IF NOT EXISTS idx_watchlist_id ON watchlist(id);
CREATE INDEX IF NOT EXISTS idx_watchlist_user_id ON watchlist(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_content_id ON watchlist(content_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_user_content ON watchlist(user_id, content_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_priority ON watchlist(priority);
CREATE INDEX IF NOT EXISTS idx_watchlist_added_at ON watchlist(added_at);

-- Уникальность комбинации user_id + content_id (один контент в списке один раз)
ALTER TABLE watchlist ADD CONSTRAINT unique_watchlist_item 
    UNIQUE (user_id, content_id);

-- ============================================
-- Тестовые данные (опционально, только для разработки)
-- ============================================

-- Категории
INSERT INTO categories (name, description) VALUES
    ('Фильмы', 'Полнометражные художественные фильмы'),
    ('Сериалы', 'Многосерийные телевизионные проекты'),
    ('Аниме', 'Японская анимация'),
    ('Документальные', 'Документальные фильмы и сериалы')
ON CONFLICT (name) DO NOTHING;

-- Пользователь для тестов (Telegram тестовый ID)
INSERT INTO users (telegram_id, username, first_name, last_name) 
VALUES ('5206838876', 'test_user', 'Иван', 'Тестов')
ON CONFLICT (telegram_id) DO NOTHING;

-- Фильмы для тестов
INSERT INTO view_history (user_id, content_id, watched_at, rating, notes)
VALUES (
    (SELECT id FROM users WHERE telegram_id = '5206838876'),  -- ID пользователя
    (SELECT id FROM content WHERE title = 'Человек-паук'),        -- ID контента
    CURRENT_TIMESTAMP,                                      -- Время просмотра
    9.5,                                                    -- Оценка (1-10)
    'Отличный фильм! Пересматривал второй раз.'            -- Заметки
);

-- Для сериала (с указанием сезона и эпизода)
INSERT INTO view_history (user_id, content_id, watched_at, season, episode, episode_title, rating)
VALUES (
    (SELECT id FROM users WHERE telegram_id = '5206838876'),
    (SELECT id FROM content WHERE title = 'Игра Престолов'),
    CURRENT_TIMESTAMP,
    1,                         -- Сезон
    1,                         -- Эпизод
    'Зима близко',             -- Название эпизода
    9.0
);
INSERT INTO content (
    title, 
    original_title, 
    description, 
    content_type, 
    release_year, 
    duration_minutes,
    imdb_rating,
    imdb_id,
    genre,
    director,
    language,
    country,
    category_id
) VALUES 
    (
        'Начало',
        'Inception',
        'Сон внутри сна внутри сна...',
        'movie',
        2010,
        148,
        8.8,
        'tt1375666',
        'Фантастика, Боевик',
        'Кристофер Нолан',
        'Английский',
        'США, Великобритания',
        (SELECT id FROM categories WHERE name = 'Фильмы')
    ),
    (
        'Игра Престолов',
        'Game of Thrones',
        'Борьба за Железный Трон Семи Королевств',
        'series',
        2011,
        NULL,
        9.2,
        'tt0944947',
        'Фэнтези, Драма',
        'Дэвид Бениофф, Д. Б. Уайсс',
        'Английский',
        'США',
        (SELECT id FROM categories WHERE name = 'Сериалы')
    )
ON CONFLICT (imdb_id) DO NOTHING;

-- ============================================
-- Сообщение об успешной инициализации
-- ============================================
DO $$
BEGIN
    RAISE NOTICE '✅ База данных Movie Tracker успешно инициализирована';
    RAISE NOTICE '📊 Создано таблиц: 5 (users, categories, content, view_history, watchlist)';
    RAISE NOTICE '👤 Тестовый пользователь: telegram_id=123456789, username=test_user';
    RAISE NOTICE '🎬 Тестовый контент: "Начало" (фильм), "Игра Престолов" (сериал)';
END $$;
