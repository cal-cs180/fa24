#!/usr/bin/perl -T

# uploads a file and saves it

# 03/21/05 - Initial creation - kevinm
# 11/16/21 - cleaned up perl code and made sure that all indents are correct - mars
# 11/17/21 - normalized variable names so that the script is not nearly as confusing as it was -mars

use CGI qw/:standard/;
use CGI::Carp 'fatalsToBrowser';        # echo fatal error messages to browser
use Cwd;
use JSON;
print header('application/json');

$CGI::DISABLE_UPLOADS = 0;              # allow uploads

# For security reasons lets limit this script to binaries
# located in either /bin or /usr/bin

$ENV{'PATH'} = '/bin:/usr/bin';

require 'ctime.pl';

$cgi		= new CGI;
my $json = new JSON;
@pgm		= split ('/', $0);
$pgm		= $pgm[$#pgm];
$maxMB		= 200; 				# max file size in MB
$proj_id	= &untaint ($cgi->param('project_number'));
$unzip_folderss =~ s/\.zip//;

# Make sure that the person contacting us knows the shared secret... not amazing web security but passable for now
if ($cgi->param('secret') and ($cgi->param('secret') eq 'LXYt7WAsZKjRP2w9a')) {  #update this to match the secretat on the run test.py
  $secret = $cgi->param('secret');
} else {
  exit;
}

# derive the UNIX path and URL to the output directory
# set access for the "here" button depending on the directory permissions

($saveDIR	= &untaint (getcwd)) =~ s/\/ssl$/\/files\/proj$proj_id/i;

$server		= $ENV{'SERVER_NAME'};
$server_request = 'https://' . $server . $ENV{'REQUEST_URI'};
$user		= 'unknown_user';
if ($cgi->param('user_id')) {
  $user = $cgi->param('user_id');
}
$mode		= (stat($saveDIR))[2]; 	# perms of the output dir
$mode		= sprintf("0%o", $mode & 07777);

# We need a user to be defined. This is taken care of by the browser
# environment and this comes using .htaccess for authentication
# If we don't have a user then push an error web page and exit
# from the script

if (not $user) {
  &webpage ("Authentication error: Unable to determine a valid user.");
  exit;
}

# if files are world-readble on UNIX may still invoke files/.htaccess
# use my login setup for classes to allow access
# it invokes ~/public_html/login/SSL/.htaccess

$server_request;

if ( $mode =~ /^(.*?)[1234567]$/ ) {
  ($saveURL 	= $server_request) =~ s/\/ssl\/${pgm}$/\/files\/proj$proj_id/i;
} else {					
  $saveURL	= $server_request . "/~$owner/login/SSL/?file=$saveDIR";
}

$saveURL	= &untaint ($saveURL);

if ($cgi->param('uploaded_file')) {
  $filename = $cgi->param('uploaded_file');
  my @list = &readfile ($filename);
  print $json->encode(\@list);
} else {
  my @list = ("No file uploaded",);
  print $json->encode(\@list);
  #&webpage ("No file uploaded for user $user to $saveDIR with unzip folder $unzip_folderss ");
}
exit;

#######################################################################
# print &readfile ($filename);
#######################################################################
sub readfile
{
  my ($file)	= @_;
  my ($ext)	= $file;

  my $downloaded_file;

  if (!$downloaded_file && $cgi->cgi_error) {
     return ($cgi->cgi_error);
  }

  # derive the output filename
  my $save	= &untaint ("$user.zip");
  #my $html_top	= "<body bgcolor='#FFFFCC'>\n";
  #my $html_end	= "</body>\n";
  my $size	=  (stat($file))[7];
  my $message 	= '';

  if ( $size > ($maxMB * 1000000) ) {
    $message 	= "Unable to upload $file!<p>\n"
	 	. "Exceeds Maximum file size $maxMB MB<p>\n"
		. "\n";
  } else {
    $downloaded_file	= $cgi->upload('uploaded_file');

    my $fi = "$saveDIR/$save";

    my $unzip_folder = $fi;
    $unzip_folder =~ s/\.zip//;

    if ( CORE::fc($unzip_folder) eq CORE::fc($saveDIR) ) {
        #&webpage ("Fatal Error: We don't have a unique path to extract the uploaded file into.");
        return ("Fatal error: $user $unzip_folder $saveDIR");
    }

    # Let's check now if the directory exists. If yes then remove the directory

    if (-e $unzip_folder) {
	unlink $unzip_folder;
	system("rm -rf $unzip_folder");
    }

    open (FILE, ">$saveDIR/$save") || print "file open error ($saveDIR/$save)";
    chmod (0444, "$saveDIR/$save");
    print FILE <$downloaded_file>;
    close FILE;

    system("unzip -q $saveDIR/$save -d $unzip_folder");
    system("rm -rf $saveDIR/$save");

    $message	= "$user uploaded $file, with file size $size bytes. "
		. "The uploaded file was renamed $save and extracted here: $saveURL/$user. "
	. "You can access other student $proj_id projects here: $saveURL\n";

#	. "unzip_folder = $unzip_folder\n<p>"
#		. "saveDIR = $saveDIR\n<p>"
#		. "fi = $fi<p>\n"
#		. "save = $save<p>\n"
#		. "downloaded_file = $downloaded_file";

    close $downloaded_file;
  }
  return ($message, "$file", $size, "$saveURL/$user");
}

#######################################################################
# &webpage ("some message");
#######################################################################
sub webpage
{
  my ($message) = @_;
  chop($now	= &ctime(time()));
  my $admin	= 'inst@eecs.berkeley.edu';
  my $adminurl	= "<a href='mailto:$admin'>$admin</a>";
  my $font	= "font size='2'";
  my $tdr	= "td valign='center' align='right'";
  my $tdl	= "td valign='center 'align='left'";
  my $tdc	= "td valign='center' align='center'";

  my $header 	=
	"Content-type: text/html\n\n" .
	"<html><head>\n" .
        "<title>File Upload Site</title>\n";

	open (FILE,"/share/b/pub/html/header.html");

        while ( <FILE> ) { $header .= $_; }
        close FILE;

  my $footer	=
        "<hr>\n" .
        "<table width='100%'>\n" .
        "<tr>\n" .
        "  <$tdl><$font> $adminurl </font></td>\n" .
        "  <$tdc><$font> &nbsp; </font></td>\n" .
        "  <$tdr><$font> $now </font></td>\n" .
        "</tr>\n" .
        "</table>\n" .
        "</body></html>";

	print "$header<p>$message<p>\n$footer";
}

############################################################################
# $string = &untaint($string);
# "\\000-\\177";                                # 7-bit (printable) chars
# "\\012|\\015|\\040-\\074|\\076|\\078-\\177";  # excludes ?, =
############################################################################
sub untaint
{
  my ($line) = @_;
  my $CHARS = "\\012|\\015|\\040-\\177";                # selected chars

  if ($line =~ m/(^[$CHARS]*$)/gi) {
     return $1
  }
else {
  return "can't untaint '$line" };
}
