import sys

class Field:

	def __init__(self, name="", size=0, default_value=0):
		self.name = name										#name of the field
		self.size = size										#size in bits
		self.default_value = default_value 						#default value for the field

		if name == "" or size == 0:
			print("ERROR!\nThe field need a valid name and a size > 0")
			sys.exit()

		


class Header:

	def __init__(self, name = "", size=0):
		self.name = name										#name of the header
		self.size = size										#header total_len
		self.fields = []										#list of all header fields

		if name == "" or size ==0:
			print("ERROR!\nThe header need a valid name and a size > 0")
			sys.exit()

		if self.size % 8 != 0:
			print("ERROR!\nThe header size needs to be byte aligned")
			sys.exit()

	def validHeader(self):
		if self.size <= 0 or len(self.fields) == 0:
			print("Invalid header size\n")
			return False
		
		counter = 0
		for field in self.fields:
			counter = counter + field.size

		if counter != self.size:
			print(f"Invalid header size (header {self.name})")
			return False

		return True

	#check if the field is valid field or a list of valid fields, and add in the list fields
	def addField(self, field):	
		if isinstance(field, Field) or isinstance(field, list):

			if isinstance(field, list):

				if len(field) ==0:
					print("ERROR! The list of fields is invalid!")
					sys.exit()

				for fi in field:
					if not isinstance(fi, Field):
						print("ERROR! The list of fields is invalid!")
						sys.exit()

				self.fields.extend(field)

			else:
				self.fields.append(field)


			#print("Sucessfull!")

		else:
			print("ERROR! The list of fields is invalid!")
			sys.exit()


	def printHeader(self):

		print(f"\nheader {self.name} {{")
		for i in self.fields:
			print(f"\tbit<{i.size}> {i.name};")

		print("}")


	
