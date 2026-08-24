# Evaluation sets

Printed arena sheets used to test the event classifier end to end: each PDF is a
full set of five event images laid out as they appear on the arena, so the
detection and classification pipeline can be exercised without setting the
physical arena up.

`expected_labels.txt` records the correct class at each location (A–E) for all
three sets — compare it against what `event_detection.py` prints.
