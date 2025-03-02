from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Tải tokenizer và mô hình
model_name = "t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Chuẩn bị dữ liệu đầu vào
input_text = "translate English to French: The house is wonderful."
inputs = tokenizer(input_text, return_tensors="pt")

# Dự đoán
outputs = model.generate(inputs["input_ids"], max_length=50)
output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

model.save_pretrained("./my_model/model")
tokenizer.save_pretrained("./my_model/tokenizer")

print("Input:", input_text)
print("Output:", output_text)