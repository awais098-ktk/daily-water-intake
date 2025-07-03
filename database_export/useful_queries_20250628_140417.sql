-- Water Intake Tracker - Useful SQL Queries
-- Copy and paste these into your SQLite browser

-- 1. View all users and their daily goals
SELECT id, username, email, daily_goal, preferred_unit, theme, gender
FROM user
ORDER BY join_date DESC;

-- 2. Recent water logs with user and drink type info
SELECT 
    wl.timestamp,
    u.username,
    wl.amount,
    dt.name as drink_type,
    c.name as container_name,
    wl.input_method,
    wl.notes
FROM water_log wl
JOIN user u ON wl.user_id = u.id
LEFT JOIN drink_type dt ON wl.drink_type_id = dt.id
LEFT JOIN container c ON wl.container_id = c.id
ORDER BY wl.timestamp DESC
LIMIT 50;

-- 3. Daily water intake summary by user
SELECT 
    u.username,
    DATE(wl.timestamp) as date,
    SUM(wl.amount) as total_ml,
    COUNT(*) as log_count,
    u.daily_goal,
    ROUND((SUM(wl.amount) * 100.0 / u.daily_goal), 1) as goal_percentage
FROM water_log wl
JOIN user u ON wl.user_id = u.id
GROUP BY u.id, DATE(wl.timestamp)
ORDER BY date DESC, u.username;

-- 4. Most popular drink types
SELECT 
    dt.name,
    dt.hydration_factor,
    COUNT(wl.id) as log_count,
    SUM(wl.amount) as total_volume_ml,
    AVG(wl.amount) as avg_amount_per_log
FROM drink_type dt
LEFT JOIN water_log wl ON dt.id = wl.drink_type_id
GROUP BY dt.id
ORDER BY log_count DESC;

-- 5. Container usage statistics
SELECT 
    c.name,
    c.volume,
    u.username as owner,
    dt.name as default_drink_type,
    COUNT(wl.id) as times_used,
    SUM(wl.amount) as total_volume_logged
FROM container c
JOIN user u ON c.user_id = u.id
LEFT JOIN drink_type dt ON c.drink_type_id = dt.id
LEFT JOIN water_log wl ON c.id = wl.container_id
GROUP BY c.id
ORDER BY times_used DESC;

-- 6. Google Fit wearable connections status
SELECT 
    u.username,
    wc.platform,
    wc.platform_user_id,
    wc.is_active,
    wc.connected_at,
    wc.last_sync,
    wc.token_expires_at
FROM wearable_connections wc
JOIN user u ON wc.user_id = u.id
ORDER BY wc.connected_at DESC;

-- 7. Activity data from wearables
SELECT 
    ad.date,
    u.username,
    wc.platform,
    ad.steps,
    ad.distance_meters,
    ad.calories_burned,
    ad.active_minutes,
    ad.heart_rate_avg,
    ad.heart_rate_max
FROM activity_data ad
JOIN user u ON ad.user_id = u.id
JOIN wearable_connections wc ON ad.connection_id = wc.id
ORDER BY ad.date DESC;

-- 8. Weekly water intake trends
SELECT 
    u.username,
    strftime('%Y-W%W', wl.timestamp) as week,
    SUM(wl.amount) as weekly_total_ml,
    COUNT(*) as weekly_logs,
    AVG(wl.amount) as avg_per_log,
    (SUM(wl.amount) / 7.0) as daily_average
FROM water_log wl
JOIN user u ON wl.user_id = u.id
GROUP BY u.id, strftime('%Y-W%W', wl.timestamp)
ORDER BY week DESC, u.username;

-- 9. Input method analysis
SELECT 
    input_method,
    COUNT(*) as usage_count,
    SUM(amount) as total_volume,
    AVG(amount) as avg_amount,
    ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM water_log)), 2) as percentage
FROM water_log
GROUP BY input_method
ORDER BY usage_count DESC;

-- 10. User activity correlation (water vs steps)
SELECT 
    u.username,
    DATE(wl.timestamp) as date,
    SUM(wl.amount) as water_ml,
    ad.steps,
    ad.calories_burned,
    ad.active_minutes
FROM water_log wl
JOIN user u ON wl.user_id = u.id
LEFT JOIN activity_data ad ON u.id = ad.user_id AND DATE(wl.timestamp) = ad.date
GROUP BY u.id, DATE(wl.timestamp)
HAVING ad.steps IS NOT NULL
ORDER BY date DESC;

-- 11. Food logging data (if available)
SELECT 
    ml.timestamp,
    u.username,
    ml.food_name,
    ml.quantity_g,
    ml.calories,
    ml.meal_type,
    ml.input_method
FROM meal_logs ml
JOIN user u ON ml.user_id = u.id
ORDER BY ml.timestamp DESC
LIMIT 50;

-- 12. Database overview - record counts
SELECT 
    'Users' as table_name, COUNT(*) as record_count FROM user
UNION ALL SELECT 'Water Logs', COUNT(*) FROM water_log
UNION ALL SELECT 'Drink Types', COUNT(*) FROM drink_type
UNION ALL SELECT 'Containers', COUNT(*) FROM container
UNION ALL SELECT 'Wearable Connections', COUNT(*) FROM wearable_connections
UNION ALL SELECT 'Activity Data', COUNT(*) FROM activity_data
UNION ALL SELECT 'Food Items', COUNT(*) FROM food_items
UNION ALL SELECT 'Meal Logs', COUNT(*) FROM meal_logs
ORDER BY record_count DESC;
