START TRANSACTION;

-- 1) History tied to connections
DELETE ch
FROM guacamole_connection_history ch
JOIN guacamole_connection c USING (connection_id);

-- 2) Sharing profile perms/params tied to those connections
DELETE spp
FROM guacamole_sharing_profile_permission spp
JOIN guacamole_sharing_profile sp USING (sharing_profile_id)
JOIN guacamole_connection c ON c.connection_id = sp.primary_connection_id;

DELETE sppar
FROM guacamole_sharing_profile_parameter sppar
JOIN guacamole_sharing_profile sp USING (sharing_profile_id)
JOIN guacamole_connection c ON c.connection_id = sp.primary_connection_id;

DELETE sp
FROM guacamole_sharing_profile sp
JOIN guacamole_connection c ON c.connection_id = sp.primary_connection_id;

-- 3) Connection perms/params
DELETE cp
FROM guacamole_connection_permission cp
JOIN guacamole_connection c USING (connection_id);

DELETE p
FROM guacamole_connection_parameter p
JOIN guacamole_connection c USING (connection_id);

-- 4) Connections
DELETE FROM guacamole_connection;

-- (Optional) Also clear connection groups
DELETE FROM guacamole_connection_group_permission;
DELETE FROM guacamole_connection_group;

COMMIT;
