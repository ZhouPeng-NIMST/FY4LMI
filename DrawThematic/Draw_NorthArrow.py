#coding:utf-8

from PIL import Image, ImageDraw


def Draw_NorthArrow(outname, dstname, pastname):
    '''
    贴图：在一张图片上贴另一张图
    :param outname: 输出文件名
    :param dstname: 底图
    :param pastname: 所需贴的图
    :return: 无
    '''

    imborder = Image.open(dstname)
    imcontent = Image.open(pastname)
    target = Image.new('RGBA',imborder.size,(0,0,0,0))
    x, y = imcontent.size

    # 设置贴图的位置
    m_pos = [750, 110]
    box = (m_pos[0], m_pos[1], m_pos[0]+x, m_pos[1]+y)

    # 对贴图大小进行resize
    # imcontent = imcontent.resize((box[2] - box[0], box[3] - box[1]))
    # imcontent = imcontent.convert('RGBA')
    imborder = imborder.convert('RGBA')

    # 进行贴图...
    target.paste(imborder,(0,0),imborder)
    target.paste(imcontent, box)
    drawtarget = ImageDraw.Draw(target)

    # 在图上贴文字
    # datestr = startdate+'-'+enddate
    # font = ImageFont.truetype(cfg["Font"],18)
    # # datestr.encode('gb18030')
    #
    # drawtarget.text((32,30),strDescripe,font = font,fill=(255,255,255))
    # drawtarget.text((32,52),datestr,font = font,fill=(255,255,255))

    target.save(outname)

    return target




if __name__ == '__main__':
    pastname = 'NorthArrow.png'
    dstname = 'china.png'
    outname = r'Finaly.png'
    Draw_NorthArrow(outname, dstname, pastname)






