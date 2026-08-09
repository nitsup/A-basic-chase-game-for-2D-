# A-basic-chase-game-for-2D-
this is a basic project for a game that uses simple libraries to create a game with a player (WASD, E for shield) enemy with attack patterns, boost box, trap box, pause and start menu while tracking high scores.

# ACA Chase Game

## Overview
A Pygame chase-style action game where the player must dodge attacks, collect boosts, and survive a powerful enemy.

## Controls
- `WASD`: move the player
- `E`: activate the shield when unlocked
- `ESC`: pause or resume the game

## Mechanics
- Shield lasts 2 seconds and has a 20-second cooldown.
- Shield reflects 30 damage from ranged attacks when the player is outside close range.
- Close-range enemy attacks bypass the shield.
- The shield faces the mouse cursor.
- The shield cooldown bar gets a white outline when ready.

## Health
- Player health is displayed as pixel-art hearts.
- Each heart represents 2 half-heart HP units.
- The player starts with 10 half-heart units (5 full hearts).

## Visual polish
- The background renders as a white stony ground when no image is available.
- Enemy projectiles are rendered in grey with a darker outline.
- The player and enemy no longer have a black shadow around them.

## Notes
- The game freezes enemy movement while the player is in the dying state.
- Death animation shrinks or lowers the player into a dead state.
- A boost warning pulse appears when the boost is near expiration.

### INSTRUCTIONS TO USE

- this can be used only if you manage the environment well
- the environment in this case was made mainly by me but using AI for debugging the environment
- code has all the instructions and comments written to ensure that the code is simple to understand.
- also, the images used in this can be copy write inclusive. 
