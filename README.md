This Python project implements a team project planner tool with APIs for managing users, teams, and project boards. Data persistence is handled using local JSON files, and communication is via JSON strings.

## Usage

## Managing Users

The User class provides methods to:

-- Create a new user with unique names and display names within length limits.
-- List all existing users.
-- Describe a user by their ID.
-- Update a user's display name.
-- Retrieve teams associated with a user.

## Managing Teams

The Team class includes methods for:

-- Creating a new team with unique names.
-- Listing all teams.
-- Describing a team by its ID.
-- Updating a team's details.
-- Adding and removing users from a team.
-- Listing users within a team.

## Managing Project Boards

The ProjectBoard class supports:

-- Creating a board within a team.
-- Closing boards when all tasks are complete.
-- Adding tasks to open boards.
-- Updating task statuses.
-- Listing all open boards for a team.
-- Exporting board details to a text file for a presentable view.
