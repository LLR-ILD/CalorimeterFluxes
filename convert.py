import os

def read_and_convert_dat_file(input_file_number, outfile):
    input_file_name = 'data/StdHep/FCC/fetch_Z/pairs_{}.dat'.format(input_file_number)

    with open(input_file_name, 'r') as infile:
        lines = infile.readlines()
        # Write the total number of lines to the first line
        outfile.write(str(len(lines)) + "\n")
        for line in lines:  # Start from the first line
            # Split each line into a list of values
            values = line.split()
            
            # Assign values from the dat file to the appropriate variables
            phep4, phep1, phep2, phep3, vhep1, vhep2, vhep3 = map(float, values[:7])

            # Define your fixed variables
            isthep = 1
            jmohpe1 = jmohpe2 = jdahpe1 = jdahpe2 = 0
            idhep = 11 if phep4 > 0 else -11
            vhep4 = 0
            phep5 = 5.11e-4

            # Write the new line to the outfile
            outfile.write("{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12} {13} {14}\n".format(
                isthep, idhep, jmohpe1, jmohpe2, jdahpe1, jdahpe2, phep1, phep2, phep3, phep4, phep5, vhep1, vhep2, vhep3, vhep4))


# Define the range of file numbers
start = 1
end = 3  # Adjust as necessary

if not os.path.exists("data/StdHep/FCC/output1"):
    os.makedirs("data/StdHep/FCC/output1")
# Open the single output file
with open('data/StdHep/FCC/output1/output1.hepevt', 'w') as outfile:
    # Call the function for each file in the range
    for i in range(start, end+1):
        read_and_convert_dat_file(i, outfile)
