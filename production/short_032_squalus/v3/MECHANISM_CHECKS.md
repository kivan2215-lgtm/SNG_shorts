# Spatial and motion checks for V3

These are internal model coordinates, not measured historical engineering dimensions. The scene explains the operating principle and does not claim to reproduce exact crew positions, controls or dimensions.

- Upper handholds at x = ±0.375, y = 0.70 sit at radius ≈0.794, outside the closed hatch radius 0.65. Their front surface also clears the opened cover's y extent.
- Upper floor world height = chamber offset 0.26 + floor 2.50 = 2.76. The climbing person's final foot/root height is 2.76.
- Final transfer position (x≈0.05, y=−0.85) is outside the open floor hole (r=0.62) and inside the standing platform (r=1.72).
- The short transfer shot shows the last ladder steps, not an entire chamber-height ascent squeezed into 1.7 seconds. Feet lift separately for the step onto the platform.
- Upper hand targets are limited in height to the handholds, and release before the final backward step.
- Guide-cable work uses arm motion beside the cable; the diver no longer slides bodily across the deck.
- Lower waiting crew stand forward of the roof overhang so their faces remain visible.
- Hatch handwheels finish turning at normalized p=0.20; cover opening begins at p=0.22 and ends at p=0.85. The next transfer shot retains the opened hatch state and wheel angle.
- Dewatering geometry and the HUD level use the same quintic easing and interval [0.06, 0.83]. The water object is hidden when empty; it does not remain as a disk across the dry passage.
- Wheel rotation is composed about each wheel's local normal. A runtime invariant verifies that spinning a wheel does not change its plane. This corrected an issue found in intermediate renders.
- The water stream in the valve view curves around the open plate instead of passing straight through it.
- The lower open chamber is flooded again during ascent while the upper compartment is sealed.

Final encoded review is recorded separately in ru/v3/QC.json and en/v3/QC.json. Source-coordinate checks alone do not substitute for inspection of the delivered MP4.
