from flask import request, current_app, send_from_directory, signals
from flask_restful import Resource
from werkzeug.utils import secure_filename
from http import HTTPStatus
from pdf2image import convert_from_path
from PIL import Image
import numpy as np
import os, time
from app.conf import _init_logging
from app.tmf_errors import errorFormaterMarshmallow
from mimetypes import MimeTypes
import platform

#deletes Files in uploads Folder after request
def del_converted(*args,**kwargs):
    #print(os.curdir)
    filesinDir=os.listdir(path=current_app.config['UPLOAD_FOLDER'])
    for f in filesinDir:

        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], f))
        except:
            continue

#  Signal binding function
signals.request_finished.connect(del_converted)

#init logging
logger= _init_logging('ressource.converter')

class Convert_to_PDF(Resource):


    def post(self):

        start = time.time()
        FNR_List = current_app.config['ERRORNR']
        logger.info("Post Call for Converter started at {}".format(time.asctime(time.localtime(time.time()))))
        # get global Fehlerbildnummer Prefix as Env Variable
        FBNRPREFIX = os.environ.get('FBNRPREFIX', '80094658')


        if 'file' not in request.files:
            FNummer = FBNRPREFIX + '00000003'
            logger.error(f"http code 400, {FNR_List[3]['00000003']['message']}",
                         extra=formatLoggerInfo(FNummer, file.filename, request.url))
            return errorFormaterMarshmallow(400, 'Wrong File', None,
                                            FNR_List[3]['00000003']['message'],
                                            'Bad request', FNummer), HTTPStatus.BAD_REQUEST
        file = request.files['file']
        if not file:
            FNummer = FBNRPREFIX + '00000002'
            logger.error(f"http code 400, {FNR_List[2]['00000002']['message']}",
                         extra=formatLoggerInfo(FNummer, file.filename, request.url))
            return errorFormaterMarshmallow(400, 'Wrong File', None,
                                            FNR_List[2]['00000002']['message'],
                                            'Bad request', FNummer), HTTPStatus.BAD_REQUEST

        #Check max Content Length
        if str(request.headers['Content-Length']) > '4000000':
            FNummer = FBNRPREFIX + '00000006'
            logger.warning(f"http code 413, {FNR_List[6]['00000006']['message']}",
                         extra=formatLoggerInfo(FNummer, file.filename, request.url))
            return errorFormaterMarshmallow(413, 'File to big', None,
                                            FNR_List[6]['00000006']['message'],
                                            'REQUEST_ENTITY_TOO_LARGE', FNummer), HTTPStatus.REQUEST_ENTITY_TOO_LARGE


        #secure Filenam:
        # Pass it a filename and it will return a secure version of it. This filename can then safely be stored on a
        # regular file system and passed to os.path.join(). The filename returned is an ASCII only string for maximum portability.
        filename = secure_filename(file.filename)

        #save requested File in Upload Folder
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],filename))
        #to have a Pointer to the File stored in Upload Folder
        filepath= (os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        #Check which MimeTypes did we received
        mime=MimeTypes()
        mime_type= mime.guess_type(filepath)
        mime_type=mime_type[0]

        if mime_type not in current_app.config['ALLOWED_EXTENSIONS']:
            FNummer = FBNRPREFIX + '00000001'
            logger.error(f"http code 400, {FNR_List[1]['00000001']['message']}",
                         extra=formatLoggerInfo(FNummer, file.filename, request.url))
            return errorFormaterMarshmallow(400, 'Wrong File', None,
                                            FNR_List[1]['00000001']['message'],
                                            'Bad request', FNummer), HTTPStatus.BAD_REQUEST

        # Now some Parameters for converter:
        # because jpegs, pdfs and pngs have no alpha-channel, W gets set to 1
        # otherwise, if alpha-channel, it must get used in the non-linear transfer function
        # rgb_out = W * rgb_in ^(1 / gamma)
        W = 1
        # gamma should be in (0.950 < γ < 0.995 or 1.005 < γ < 1.050)
        # which will modify just the least significant bits, to remove steganography
        gamma = 1.01
        if mime_type=="application/pdf":
            neutralized_pdf= pdf_to_pdf(filepath,filename, W, gamma,FNR_List,FBNRPREFIX)
        else:
            neutralized_pdf = picture_to_pdf(filepath, filename, W, gamma,FNR_List,FBNRPREFIX)

        #Check result. In case that in previous Methods happend Issues, we return now
        if 'tuple' in str(type(neutralized_pdf)):
            return neutralized_pdf

        ende = time.time()
        logger.info("Post Call execution time {:5.3f}s".format(ende - start))

        #print(f"Betriebssystem auf dem ich laufe: {platform.platform()}")

        if "Windows" in platform.platform():
            dir = r".\uploads"
            return send_from_directory(dir, filename=neutralized_pdf, as_attachment=True)
        else:
            dir = r"./uploads"
            return send_from_directory(dir, path=dir, filename=neutralized_pdf, as_attachment=True)

def pdf_to_pdf(filepath,filename,W,gamma,FNR_List,FBNRPREFIX):

    try:
        if "Windows" in platform.platform():
            images = convert_from_path(filepath, 100,poppler_path=r'.\app\poppler-0.68.0\bin')
        else:
            images = convert_from_path(filepath, 100)
    except:
        FNummer = FBNRPREFIX + '00000004'
        logger.error(f"http code 400, {FNR_List[4]['00000004']['message']}",
                     extra=formatLoggerInfo(FNummer, filename, request.url))
        return errorFormaterMarshmallow(400, 'Can not read PDF with PIL', None,
                                            FNR_List[4]['00000004']['message'],
                                            'Bad request', FNummer), HTTPStatus.BAD_REQUEST

    pil_img = []
    # for every image which was stored as a page in the pdf
    for i in range(len(images)):
        # put one image into the numpy-array
        im = np.array(images[i])
        # non-linear transformation
        im_out = W * (im) ** (1 / gamma)
        # put im_out into the image format and append to the pil_image-array
        pil_img.append(Image.fromarray(np.uint8(im_out)))

    #definition of target Filename
    neutral_pdf = "{}{}".format('neutralized-',filename)
    # save all images in one pdf
    pil_img[0].save(os.path.join(current_app.config['UPLOAD_FOLDER'],neutral_pdf), format='PDF',save_all=True, append_images=pil_img[1:])
    #delete File from Request
    os.remove(filepath)
    return neutral_pdf

def picture_to_pdf(filepath,filename, W, gamma,FNR_List,FBNRPREFIX):
    try:
        image = Image.open(filepath)
    except:
        FNummer = FBNRPREFIX + '00000005'
        logger.error(f"http code 400, {FNR_List[5]['00000005']['message']}",
                     extra=formatLoggerInfo(FNummer, filename, request.url))
        return errorFormaterMarshmallow(400, 'Can not read PDF with PIL', None,
                                        FNR_List[5]['00000005']['message'],
                                        'Bad request', FNummer), HTTPStatus.BAD_REQUEST

    # put one image into the numpy-array
    im = np.array(image)
    # non-linear transformation
    im_out = W * (im)**(1 / gamma)
    # put im_out into the image format
    pil_img = Image.fromarray(np.uint8(im_out))

    #definition of target Filename
    neutral_pdf = "{}{}".format('neutralized-',filename)

    pil_img.save(os.path.join(current_app.config['UPLOAD_FOLDER'],neutral_pdf))
    # delete File from Request
    os.remove(filepath)
    return neutral_pdf

def formatLoggerInfo(FNummer,json_data,requesturl):
     return {"fehlerbildnummer": FNummer,"incomming_message": json_data,"communication_pattern": "req-reply"
         ,"service_domain": "giga-infra","service_call": requesturl}