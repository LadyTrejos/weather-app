#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <number_of_iterations> <sensor_name>"
    exit 1
fi

echo "Running script"
number_of_iterations=$1
sensor_name=$2

for ((i=1; i<=number_of_iterations; i++)); do
    echo $'\n\n'
    printf '*%.0s' {1..100}; echo

    temperature=$(awk -v min=20 -v max=30 'BEGIN{srand(); printf "%.2f\n", min+rand()*(max-min)}')
    current_date=$(date +"%d/%m/%Y %H:%M:%S.%3N")

    echo "Executing the script ($i/$number_of_iterations) with temperature: $temperature and sensor name: $sensor_name at $current_date"$'\n'

    weather set temperatura $temperature $sensor_name "$current_date" --username my_key
    sleep "$(echo "scale=6; 0.001" | bc)"
done

printf '*%.0s' {1..100}; echo
echo "Execution completed"
