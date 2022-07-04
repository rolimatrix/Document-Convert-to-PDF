# coding=utf-8
def errorFormaterMarshmallow(httpcode, message, error_class=None, reason=None, status=None, referenceError=None):
    if error_class is not None:
        error_message = error_class.messages
        for key, value in error_message.items():
            Feld= key
            values= str(value)
        # these signs are not looking well
        values = values.replace("[","")
        values = values.replace("]", "")

        return { "code": httpcode,
            "reason": "{}: {}".format(Feld, values),
            "message": message,
            "status": status,
            "referenceError":referenceError}
    else:
       return  {"code": httpcode,
         "reason": reason,
         "message": message,
         "status": status,
         "referenceError": referenceError}