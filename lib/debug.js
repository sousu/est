// 
// debug proc
// 

var debug = function(est,config,logger){
    print_header("Test");
    
    var genre = est.genre('test');
    genre.each_entry(function(e){
        logger.debug(e.dirPath);
        var g = object(Gatherer).init(config,logger);
        var fd = object(FileDiver).init(logger);

        g.regex(e.regex, e.exregex);
        fd.set(e.dirPath, e.depth);
        fd.enum_dir(function(file){
            if((file.type == 'dir') && (file.depth == e.depth)){
                g.regist_dir(file.chain, file.path);
            }
            if((file.type == 'file')&&(file.depth <= e.depth)){
                g.regist_file(file.chain, file.path);
            }
        });
        g.each_element(function(elem){
            //logger.debug(elem.name);
            //logger.debug("\n"+elem.target);
        });
    });

};
