if "Citation" in items:
    dark = float(int(color['node'][1:], 16))
    shallow = float(int(color['label'][1:], 16))
    color_node = min(shallow + float(values[list(items).index("Citation")]) / 64. * (dark - shallow), dark)
    color_node = '#' + str(hex(int(color_node)))[-6:]
    # tmp = tmp.replace("colorNode", color_node)
    tmp = tmp.replace("colorNode", color['node'])
else:
    tmp = tmp.replace("colorNode", color['node'])