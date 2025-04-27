#!/bin/bash

# Corrected dasel command to avoid header repetition
dasel -f /clean_json/combined.json -o csv -p '[
  ["key", "component", "textRange"],
  (.issues | [.key, .component, .textRange])
]'
