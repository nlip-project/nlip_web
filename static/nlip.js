const AllowedFormats = {
  text: "text",
  token: "token",
  structured: "structured",
  binary: "binary",
  location: "location",
  generic: "generic"
}

class NLIP_MESSAGE {
  constructor(messageType, format, subformat, content, label = null, submessages = null) {
    this.messageType = messageType;
    this.format = format;
    this.subformat = subformat;
    this.content = content;
    this.label = label;
    this.submessages = submessages;
  }

  getMessageType() {
    return this.messageType;
  }

  getFormat() {
    return this.format;
  }
  
  getSubformat() {
    return this.subformat;
  }

  getContent() {
    return this.content;
  }
  
  getLabel() {
    return this.label;
  }

  getSubmessages() {
    return this.submessages;
  }

  jsonSerialize() {
    const object = {
      messageType: this.getMessageType(),
      format: this.getFormat(),
      subformat: this.getSubformat(),
      content: this.getContent(),
      label: this.getLabel(),
      submessages: this.getSubmessages()
    }
    return JSON.stringify(object);
  }
}

class NLIP_FACTORY {
  static create_text(messageType, language='English', content, label = null) {
    return new NLIP_MESSAGE(messageType, AllowedFormats.text, language, content, label);
  }

  static create_control(messageType, language, content, label = null) {
    return new NLIP_MESSAGE(messageType, AllowedFormats.text, language, content, label);
  }

  static create_token(messageType, tokenType, token, label = null) {
    return new NLIP_MESSAGE(messageType, AllowedFormats.token, tokenType, token, label);
  }

  static create_structured(messageType, contentType, content, label = null) {
    return new NLIP_MESSAGE(messageType, AllowedFormats.structured, contentType, content, label);
  }

  static create_json_structured(messageType, jsonDict, label = null) {
    return new NLIP_MESSAGE(messageType, AllowedFormats.structured, "JSON", jsonDict, label);
  }

  static create_binary(messageType, binaryType, encoding, content, label = null) {
    return new NLIP_MESSAGE(messageType, AllowedFormats.binary, `${binaryType}:${encoding}`, content, label);
  }

  static create_image(messageType, encoding, content, label = null) {
    return this.create_binary(messageType, "image", encoding, content, label);
  }

  static create_audio(messageType, encoding, content, label = null) {
    return this.create_binary(messageType, "audio", encoding, content, label);
  }

  static create_video(messageType, encoding, content, label = null) {
    return this.create_binary(messageType, "video", encoding, content, label);
  }

  static create_location_text(messageType, language, location, label = null) {
    return new NLIP_MESSAGE(messageType, AllowedFormats.location, "text", location, label);
  }

  static create_location_gps(messageType, location, label = null) {
    return new NLIP_MESSAGE(messageType, AllowedFormats.location, "gps", location, label);
  }

  static create_error(messageType, errorCode, label = null, language = 'english', errorLabel = 'errorCode:') {
    return createText(messageType, language, errorLabel + errorCode, label);
  }

  static create_generic(messageType, subformat, content, label = null) {
    return new NLIP_MESSAGE(messageType, AllowedFormats.generic, subformat, content, label);
  }
}

export { NLIP_MESSAGE, NLIP_FACTORY, AllowedFormats };