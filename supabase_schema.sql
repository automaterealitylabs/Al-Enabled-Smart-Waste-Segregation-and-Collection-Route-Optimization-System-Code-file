-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user', -- admin, driver, user
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Dumpyards Table
CREATE TABLE IF NOT EXISTS dumpyards (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    contact TEXT,
    admin_id INTEGER REFERENCES users (id),
    status TEXT DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Vehicles Table
CREATE TABLE IF NOT EXISTS vehicles (
    id SERIAL PRIMARY KEY,
    registration_number TEXT UNIQUE NOT NULL,
    vehicle_type TEXT NOT NULL,
    capacity_kg REAL NOT NULL,
    dumpyard_id INTEGER REFERENCES dumpyards (id),
    status TEXT DEFAULT 'AVAILABLE',
    current_latitude REAL,
    current_longitude REAL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Drivers Table
CREATE TABLE IF NOT EXISTS drivers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (id),
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    license_number TEXT NOT NULL,
    dumpyard_id INTEGER REFERENCES dumpyards (id),
    status TEXT DEFAULT 'AVAILABLE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Waste Reports Table (Citizen Complaints)
CREATE TABLE IF NOT EXISTS waste_reports (
    id SERIAL PRIMARY KEY,
    citizen_id INTEGER REFERENCES users (id),
    image_url TEXT NOT NULL,
    description TEXT,
    waste_type TEXT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    address TEXT,
    priority INTEGER DEFAULT 1,
    status TEXT DEFAULT 'SUBMITTED',
    assigned_dumpyard_id INTEGER REFERENCES dumpyards (id),
    assigned_vehicle_id INTEGER REFERENCES vehicles (id),
    assigned_driver_id INTEGER REFERENCES drivers (id),
    completion_proof_url TEXT,
    ai_verification_status TEXT,
    confidence_score REAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Collection Tasks Table
CREATE TABLE IF NOT EXISTS collection_tasks (
    id SERIAL PRIMARY KEY,
    dumpyard_id INTEGER REFERENCES dumpyards (id),
    vehicle_id INTEGER REFERENCES vehicles (id),
    driver_id INTEGER REFERENCES drivers (id),
    report_id INTEGER REFERENCES waste_reports (id),
    status TEXT DEFAULT 'PENDING',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Status History Table
CREATE TABLE IF NOT EXISTS status_history (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES waste_reports (id),
    status TEXT NOT NULL,
    remarks TEXT,
    changed_by INTEGER REFERENCES users (id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. Optimized Routes Log Table
CREATE TABLE IF NOT EXISTS routes (
    id SERIAL PRIMARY KEY,
    route_name TEXT NOT NULL,
    depot_lat REAL NOT NULL,
    depot_lng REAL NOT NULL,
    total_distance_km REAL NOT NULL,
    estimated_time_mins REAL NOT NULL,
    fuel_used_liters REAL NOT NULL,
    visited_bins_count INTEGER NOT NULL,
    stops_json TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. Waste Detections Table
CREATE TABLE IF NOT EXISTS waste_detections (
    id SERIAL PRIMARY KEY,
    category_name TEXT NOT NULL,
    waste_type TEXT NOT NULL,
    bin_color TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    image_path TEXT NOT NULL,
    disposal_suggestion TEXT NOT NULL,
    user_id INTEGER REFERENCES users (id),
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. Locations Table (Waste Collection Points)
CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    location_name TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    capacity_kg REAL NOT NULL DEFAULT 100.0,
    current_fill_level REAL NOT NULL DEFAULT 0.0,
    current_weight_kg REAL NOT NULL DEFAULT 0.0,
    priority INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'Normal',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 11. Waste Categories Master Table
CREATE TABLE IF NOT EXISTS waste_categories (
    id SERIAL PRIMARY KEY,
    category_name TEXT UNIQUE NOT NULL,
    waste_type TEXT NOT NULL,
    recommended_bin_color TEXT NOT NULL,
    disposal_suggestion TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- DISABLE ROW LEVEL SECURITY (Allows your backend to insert data without error)
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE dumpyards DISABLE ROW LEVEL SECURITY;
ALTER TABLE vehicles DISABLE ROW LEVEL SECURITY;
ALTER TABLE drivers DISABLE ROW LEVEL SECURITY;
ALTER TABLE waste_reports DISABLE ROW LEVEL SECURITY;
ALTER TABLE collection_tasks DISABLE ROW LEVEL SECURITY;
ALTER TABLE status_history DISABLE ROW LEVEL SECURITY;
ALTER TABLE routes DISABLE ROW LEVEL SECURITY;
ALTER TABLE waste_detections DISABLE ROW LEVEL SECURITY;
ALTER TABLE locations DISABLE ROW LEVEL SECURITY;
ALTER TABLE waste_categories DISABLE ROW LEVEL SECURITY;

-- Seed Demo Data
INSERT INTO users (id, username, email, password_hash, role) VALUES
(1, 'superadmin', 'super@admin.com', 'scrypt:32768:8:1$n4tqK43sL3wT2t2w$7f9202164478ec094c97ea8a5624773de2916b7ff2308cfd7be1315582cde4b5', 'admin'),
(2, 'dumpadmin', 'dump@admin.com', 'scrypt:32768:8:1$n4tqK43sL3wT2t2w$7f9202164478ec094c97ea8a5624773de2916b7ff2308cfd7be1315582cde4b5', 'admin'),
(3, 'driver1', 'driver@demo.com', 'scrypt:32768:8:1$n4tqK43sL3wT2t2w$7f9202164478ec094c97ea8a5624773de2916b7ff2308cfd7be1315582cde4b5', 'driver'),
(4, 'citizen1', 'citizen@demo.com', 'scrypt:32768:8:1$n4tqK43sL3wT2t2w$7f9202164478ec094c97ea8a5624773de2916b7ff2308cfd7be1315582cde4b5', 'user')
ON CONFLICT (id) DO NOTHING;

INSERT INTO dumpyards (id, name, address, latitude, longitude, contact, admin_id) VALUES
(1, 'Central Pune Dumpyard', 'Shivaji Nagar, Pune', 18.5204, 73.8567, '9876543210', 2)
ON CONFLICT (id) DO NOTHING;

INSERT INTO vehicles (id, registration_number, vehicle_type, capacity_kg, dumpyard_id, current_latitude, current_longitude) VALUES
(1, 'MH-12-AB-1234', 'Heavy Truck', 2000.0, 1, 18.5204, 73.8567)
ON CONFLICT (id) DO NOTHING;

INSERT INTO drivers (id, user_id, name, phone, email, license_number, dumpyard_id) VALUES
(1, 3, 'Ramesh Driver', '9876543211', 'driver@demo.com', 'DL-MH-2023-123', 1)
ON CONFLICT (id) DO NOTHING;

-- Seed Waste Categories
INSERT INTO waste_categories (id, category_name, waste_type, recommended_bin_color, disposal_suggestion) VALUES
(1, 'Organic (Wet)', 'Wet Waste', 'Green', 'Dispose in Green Compost Bin. Ideal for food scraps, fruit peels, and organic waste processing.'),
(2, 'Recyclable Plastic', 'Recyclable Waste', 'Blue', 'Rinse containers and place in Blue Recycling Bin. Suitable for plastic melting and remanufacturing.'),
(3, 'Dry Paper & Cardboard', 'Dry Waste', 'Blue', 'Flatten cardboard boxes and keep dry. Dispose in Blue Bin for paper pulp recycling.'),
(4, 'Recyclable Glass', 'Recyclable Waste', 'Blue', 'Clean glass containers and place in Blue Bin. Handle with care to prevent breakage.'),
(5, 'Recyclable Metal', 'Recyclable Waste', 'Blue', 'Rinse metal cans and place in Blue Bin for metal smelting and recycling.'),
(6, 'Non-Recyclable Trash', 'General Waste', 'Black', 'Dispose in Black General Waste Bin for safe landfill or municipal incineration.')
ON CONFLICT (id) DO NOTHING;

-- Seed Collection Bins / Locations
INSERT INTO locations (id, location_name, latitude, longitude, capacity_kg, current_fill_level, current_weight_kg, priority, status) VALUES
(1, 'Bin #1 - Academic Block A', 18.5204, 73.8567, 100.0, 85.0, 75.0, 4, 'Needs Collection'),
(2, 'Bin #2 - Campus Cafeteria', 18.5245, 73.8610, 150.0, 95.0, 130.0, 5, 'Overflown'),
(3, 'Bin #3 - Student Hostel Gate 1', 18.5180, 73.8520, 120.0, 70.0, 80.0, 3, 'Needs Collection'),
(4, 'Bin #4 - Library Complex', 18.5290, 73.8650, 100.0, 40.0, 35.0, 2, 'Normal'),
(5, 'Bin #5 - Sports Complex', 18.5150, 73.8590, 100.0, 90.0, 88.0, 5, 'Overflown')
ON CONFLICT (id) DO NOTHING;

-- Reset sequence generator to avoid ID collision
SELECT setval('users_id_seq', (SELECT COALESCE(MAX(id), 1) FROM users));
SELECT setval('dumpyards_id_seq', (SELECT COALESCE(MAX(id), 1) FROM dumpyards));
SELECT setval('vehicles_id_seq', (SELECT COALESCE(MAX(id), 1) FROM vehicles));
SELECT setval('drivers_id_seq', (SELECT COALESCE(MAX(id), 1) FROM drivers));
SELECT setval('locations_id_seq', (SELECT COALESCE(MAX(id), 1) FROM locations));
SELECT setval('waste_categories_id_seq', (SELECT COALESCE(MAX(id), 1) FROM waste_categories));
