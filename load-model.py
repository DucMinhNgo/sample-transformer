from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model = AutoModelForSeq2SeqLM.from_pretrained("./my_model")
tokenizer = AutoTokenizer.from_pretrained("./my_model")

# Chuẩn bị dữ liệu đầu vào
input_text = "translate English to French: The house is wonderful."
inputs = tokenizer(input_text, return_tensors="pt")

# Dự đoán
outputs = model.generate(inputs["input_ids"], max_length=50)
output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

print("Input:", input_text)
print("Output:", output_text)