import glob
path = "079_2022-10-25_Y5626227"
a = glob.glob(f"/Users/imdaredevil/Documents/{path}/**/*.mp4", recursive=True)
print(len(a))
b = glob.glob(f"/Users/imdaredevil/Documents/{path}/**/*.mov", recursive=True)
print(len(b))
f = open("files.txt", "w")
for line in a:
    print(line)
    f.write(f"{line}\n")
f.close()